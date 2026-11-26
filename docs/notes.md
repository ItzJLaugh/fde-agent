# Revenue Growth Targets #

1. - More sellers
2. - More orders
3. - Bigger orders
4. - Fewer lost customers

## Questions ##

1)  #### More Sellers ####
    - Leads on sellers that turned into deals
    - Metadata on sellers turned to deal
    ** {leads}, {closed-deals}, {seller-id} **

2)  #### More Orders ####
    - Customers that come back
    - For the customers that come back, what are they coming to buy? Who are they buying from?
    - Is there a big player seller attracting customers 
        - If true, what is metadata on the seller doing so
    ** {customer-unique-id}, {orders}, {seller-id}, {product-id} **

3)  #### Bigger Orders ####
    - Average Order Value
    - Average amount a customer spends on purchase
    - Categories, installments, etc
    ** {order-items}, {payments} **

4)  #### Fewer Lost Customers ####
    - Late delivery causing bad reviews 
    - Late delievery have fewer repeat buyers
    - Look at common words found in reviews that aren't five stars -> weight based on stars (1=biggest, 4=least) 

- customer_id is not the customer. It's a new ID for every order. The real person is customer_unique_id. If you count repeat buyers with customer_id, you get 0% repeat.
- Reviews show about 104k "rows" in wc -l, but there are about 99k reviews. Some review comments contain line breaks, and wc -l counts each one as a new row. pandas parses them correctly.
- The translation file starts with an invisible BOM character. That's why its header printed as product_category_name earlier. Read it with encoding="utf-8-sig", or the first column name won't match.
- Revenue = price + freight_value from order_items. Payments include installment amounts too, so the two totals won't exactly agree.

### Database graph ###
There are two separate datasets, and they connect only through sellers:

 MARKETING FUNNEL (acquiring sellers)          MARKETPLACE (sellers selling to customers)
 ────────────────────────────────────          ──────────────────────────────────────────
 marketing_qualified_leads  (8,000)            customers (99,441) ──┐
        │ mql_id                                                    │ customer_id
        ▼                                                           ▼
 closed_deals  (842) ── seller_id ──────────▶ sellers (3,095)    orders (99,441)
                                                  │ seller_id      │ order_id
                                                  ▼                ▼
                                            order_items (112,650) ◀┘──▶ payments (103,886)
                                                  │ product_id     └──▶ reviews (~99k)
                                                  ▼
                                            products (32,951) ──▶ category_translation (70)
                                     (geolocation: 1M rows, joins on zip prefix, optional)

      
