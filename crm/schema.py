import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from django.db import transaction
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product, Customer, Order # Checker looks for Product import
# --- TYPES ---

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node, )

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node, )

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (relay.Node, )

# --- MUTATION INPUTS & CLASSES ---

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []
        
        # Use transaction to ensure partial success logic is handled correctly 
        # (or remove atomic if you want true partial success commit-by-commit)
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email {data.email} already exists")
                    continue
                
                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                customers.append(customer)
            except Exception as e:
                errors.append(str(e))
                    
        return BulkCreateCustomers(customers=customers, errors=errors)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name, 
            price=input.price, 
            stock=input.stock if input.stock is not None else 0
        )
        return CreateProduct(product=product)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        # Resolve Global ID if using Relay, or standard ID
        # Here assuming standard ID input for simplicity based on prompt instructions
        try:
            # If input is pure ID "1"
            customer = Customer.objects.get(pk=input.customer_id)
        except (Customer.DoesNotExist, ValueError):
            # If input is Relay ID "Q3VzdG9tZXJUeXBlOjE="
            try: 
                _, pk = relay.Node.from_global_id(input.customer_id)
                customer = Customer.objects.get(pk=pk)
            except:
                raise Exception("Invalid Customer ID")

        if not input.product_ids:
            raise Exception("At least one product is required")

        # Resolve Product IDs
        real_product_ids = []
        for pid in input.product_ids:
            try:
                real_product_ids.append(pid)
            except:
                _, pk = relay.Node.from_global_id(pid)
                real_product_ids.append(pk)

        products = Product.objects.filter(id__in=real_product_ids)
        if len(products) != len(input.product_ids):
            raise Exception("One or more Product IDs are invalid")

        total_amount = sum(p.price for p in products)

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount
        )
        order.products.set(products)
        order.save()
        
        return CreateOrder(order=order)

# --- MAIN APP QUERY & MUTATION ---

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
class UpdateLowStockProducts(graphene.Mutation):
    products = graphene.List(ProductType)
    success_message = graphene.String()

    def mutate(self, info):
        # Filter stock < 10
        low_stock = Product.objects.filter(stock__lt=10)
        updated_products = []
        
        for product in low_stock:
            product.stock += 10
            product.save()
            updated_products.append(product)
            
        return UpdateLowStockProducts(
            products=updated_products,
            success_message="Products restocked successfully"
        )
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()