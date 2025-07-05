import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

interface Shippable {
    String getName();
    double getWeight();
}

abstract class Product {
    protected String name;
    protected double price;
    protected int quantity;

    public Product(String name, double price, int quantity) {
        this.name = name;
        this.price = price;
        this.quantity = quantity;
    }

    public abstract boolean isExpired();
    public boolean isAvailable(int requested) {
        return requested <= quantity;
    }
    public void reduceQuantity(int amount) {
        quantity -= amount;
    }

    public String getName() { return name; }
    public double getPrice() { return price; }
    public int getQuantity() { return quantity; }
}

class RegularProduct extends Product {
    public RegularProduct(String name, double price, int quantity) {
        super(name, price, quantity);
    }

    @Override
    public boolean isExpired() {
        return false;
    }
}

class ExpirableProduct extends Product implements Shippable {
    private Date expiryDate;
    private double weight;

    public ExpirableProduct(String name, double price, int quantity, Date expiryDate, double weight) {
        super(name, price, quantity);
        this.expiryDate = expiryDate;
        this.weight = weight;
    }

    @Override
    public boolean isExpired() {
        return expiryDate.before(new Date());
    }

    @Override
    public double getWeight() { return weight; }
    @Override
    public String getName() { return name + " " + (int)(weight * 1000) + "g"; }
}

class ShippableProduct extends RegularProduct implements Shippable {
    private double weight;

    public ShippableProduct(String name, double price, int quantity, double weight) {
        super(name, price, quantity);
        this.weight = weight;
    }

    @Override
    public double getWeight() { return weight; }
    @Override
    public String getName() { return name + " " + (int)(weight * 1000) + "g"; }
}

class Customer {
    private String name;
    private double balance;

    public Customer(String name, double balance) {
        this.name = name;
        this.balance = balance;
    }

    public double getBalance() { return balance; }
    public void deduct(double amount) { balance -= amount; }
    public String getName() { return name; }
}

class CartItem {
    Product product;
    int quantity;

    public CartItem(Product product, int quantity) {
        this.product = product;
        this.quantity = quantity;
    }
}

class Cart {
    private List<CartItem> items = new ArrayList<>();

    public void add(Product product, int quantity) {
        if (product.isExpired()) {
            throw new IllegalArgumentException(product.getName() + " is expired.");
        }
        if (!product.isAvailable(quantity)) {
            throw new IllegalArgumentException("Not enough stock for " + product.getName());
        }
        items.add(new CartItem(product, quantity));
    }

    public void checkout(Customer customer) {
        if (items.isEmpty()) {
            throw new IllegalStateException("Cart is empty");
        }

        double subtotal = 0;
        List<Shippable> shippables = new ArrayList<>();

        for (CartItem item : items) {
            Product p = item.product;
            if (p.isExpired()) {
                throw new IllegalStateException(p.getName() + " is expired.");
            }
            if (!p.isAvailable(item.quantity)) {
                throw new IllegalStateException("Not enough stock for " + p.getName());
            }

            subtotal += item.quantity * p.getPrice();
            if (p instanceof Shippable) {
                for (int i = 0; i < item.quantity; i++) {
                    shippables.add((Shippable) p);
                }
            }
        }

        double shipping = shippables.isEmpty() ? 0 : 30;
        double total = subtotal + shipping;

        if (customer.getBalance() < total) {
            throw new IllegalStateException("Insufficient balance.");
        }

        for (CartItem item : items) {
            item.product.reduceQuantity(item.quantity);
        }
        customer.deduct(total);

        if (!shippables.isEmpty()) {
            ShippingService.send(shippables);
        }

        System.out.println("** Checkout receipt **");
        for (CartItem item : items) {
            System.out.printf("%dx %s @ %.0f = %.0f\n",
                item.quantity, item.product.getName(), item.product.getPrice(), item.product.getPrice() * item.quantity);
        }
        System.out.println("----------------------");
        System.out.printf("Subtotal %.0f\n", subtotal);
        System.out.printf("Shipping %.0f\n", shipping);
        System.out.printf("Amount %.0f\n", total);
        System.out.printf("Balance after payment: %.0f\n", customer.getBalance());
    }
}

class ShippingService {
    public static void send(List<Shippable> items) {
        System.out.println("** Shipment notice **");
        Map<String, Integer> nameCount = new LinkedHashMap<>();
        double totalWeight = 0;

        for (Shippable item : items) {
            nameCount.put(item.getName(), nameCount.getOrDefault(item.getName(), 0) + 1);
            totalWeight += item.getWeight();
        }

        for (String name : nameCount.keySet()) {
            System.out.printf("%dx %s\n", nameCount.get(name), name);
        }
        System.out.printf("Total package weight %.1fkg\n", totalWeight);
    }
}

public class Main {
    public static void main(String[] args) {
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
            Date futureDate = sdf.parse("2025-12-31");

            Customer customer = new Customer("Ahmed", 5000);

            Product cheese = new ExpirableProduct("Cheese", 150, 5, futureDate, 0.2);
            Product biscuits = new ExpirableProduct("Biscuits", 250, 3, futureDate, 0.7);
            Product scratchCard = new RegularProduct("Scratch Card", 50, 10);
            Product tv = new ShippableProduct("TV", 8000, 2, 8.0);

            Cart cart = new Cart();
            cart.add(cheese, 2);
            cart.add(biscuits, 1);
            cart.add(scratchCard, 1);

            cart.checkout(customer);
        } catch (ParseException e) {
            System.out.println("Date parse error.");
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}



