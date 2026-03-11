# Buyers club/ food coop schema
- Sort of an two-column accounting style of tracking products
- We will have multiple vendors that we are tracking and those vendors will be sources of our products
- we will be keeping track of the prices that different vendors are selling things at and want to track that history
- we will have an etl system for pulling in vendor price lists where we have automatd ways to check for price chnages and update accordingly

## contacts
  - standard contact list
  - contacts can be entities or inddividuals
  - should be able to track email, phone and address if available
  - should be used to link to vender/supplier accounts as well as members - would be great if a person could be both a vendor as well as a member and not need multiple contacts/accounts
  - this is a once source of truth for contact information

## users
  - track users of the system. Users should be an extension of contacts, not all contacts will be users
  - users will be used to track data changes
  - users should be tied to a specific email that we can send verification codes to

## vendors/suppliers
  - we will need a label and description (jsonb)
  - I want a way to track a minimum purchase price so if we are drop shipping we will know how many orders we need before we can submit an order
  - We should also track the ordering process and contact information

## members
  - thsee are all the current membors of the buyers club, the buyers
  - should link to the contacts
  - should include something that reflects their standing like tracking how much of the dues they have paid
  -

## products
  - the products table will be our canonical table of all procucts
  - it should have a unique identifier (identity)
  - it shoudl contain both a label (text) and description (jsonb, document model)

## our product skus
- our list of pruducts and sizes and prices that we sell
  - link to the products  and the unique id builds off of the product unique id
  - basic sku information like size/amount etc
  - should include different costs, for example - wholesale price, member price, non-member price and maybe something that reflects the processing cost - that is either the time or money it takes to make sellable
  - this will likely be our selling list though we may want to think about whether we want to track the price that we sold it at, if we do we would want something more like a type-2 scd approach.
  - a flag that lets us set whether this could be listed in our store even though we dont have any inventory

## our product price history
- store the history as our price changes

## locations
  - this is where our stock is - probably one location to start
  - label & description (jsonb)

## inventory table
  - this will be what we have on hand at any given time
  - probably link to the project skus
  - link to the location
  - amount on hand


## vendor products
- a list of products, sizes and price that are available from our vendors that we can order
- I think these should link to our products list
- unique vendor identifier
- price information (how do we want to track multiple prices, like wholesale vs retail?)

## vendor price history
- i am thinking when our system updates a vendor product and the price changes we would save the old price information in the history table. Though we may want to do a type-2 scd pattern here as well

## vendor purchases
- our tracking of what we purchase from vendors with a link to the product cost etc

## member/contact purchase/orders
- these are the transactions of our products going out to the people that purchase them
- should link to the price that they paid

## member/contact payments
- should these be tied to the purchases or could this all just be an accounting system or debits and credits
