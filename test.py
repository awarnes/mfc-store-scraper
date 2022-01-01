# import json, re



# with open('./hummingbird_products.json') as jsonfile:
#     stuff = json.load(jsonfile)

#     count = 0
#     list_of_things = list()
#     for product in stuff:
#         for variant in product['variants']:
#             match = re.search(r'(\d+)\s?[x]', variant['option1'])
#             if match:
#                 count += 1
#                 print(match)
#                 list_of_things.append(variant['option1'])


#     print(count)
#     print(set(list_of_things))
#     print(len(set(list_of_things)))

#     {
#     'Case of 6 x 5.5 lb / 1/2 gal Jars': '5.5 lb / 1/2 gal Jar',
#     'case of 6 x 51 oz can': '51 oz can',
#     'Case of 12 x 32 oz round glass decanters': '32 oz round glass decanter',
#     'Case of 12 x 1lb Jars': '1 lb jar',
#     'case of 8 x 2.5 oz bags': '2.5 oz bag',
#     'case of 10 x 2 lb bags': '2 lb bag',
#     'Case of 12 x 12 oz flat glass bottles': '12 oz flat glass bottle',
#     'Case of 12 x 3 oz tins': '3 oz tin',
#     '10 x  ½ oz Stand-Up Pouch': '½ oz Stand-Up Pouch',
#     'Case of 12 x 5 oz glass bottles': '5 oz glass bottle',
#     'case of 6 x 1 lb bags': '1 lb bag',
#     'case of 12 x 1 lb jar': '1 lb jar',
#     '16 lb case (4x4lb bags)': '4 lb bag',
#     '20 lb case (4x5 lb bag)': '5 lb bag',
#     'Case of 12 x 1lb jars': '1 lb jar',
#     'Case of 12 x 16 fl oz Jar': '16 fl oz jar',
#     '10 x  ½ oz Stand-up Pouch': '½ oz Stand-up Pouch',
#     '6 x 6 oz bags': '6 oz bag',
#     '4 x 5 lb bags': '5 lb bag',
#     'case of 6 x 6 oz bags': '6 oz bag',
#     'case of 6 x 1/2 lb bags': '1/2 lb bag',
#     'Case of 12 x 16 oz round glass decanters': '16 oz round glass decanter',
#     'case of 6 x 12oz bags': '12 oz bag',
#     'Case of 12 x 1 lb Jar': '1 lb jar',
#     'Case of 12 x 1 lb jars': '1 lb jar',
#     '20 lb case (4x5lb bags)': '5 lb bag',
#     'Case of 6 x 5.5 lb /1/2 gal Jars': '5.5 lb / 1/2 gal Jar',
#     'Case of 6 x 1/2 gal Glass Jugs': '1/2 gal glass jug',
#     '12 x 8.5 fl oz bottles': '8.5 fl oz bottle',
#     'case of 10 x 4 oz bag': '4 oz bag',
#     'Case of 12 x 2 oz tins': '2 oz tin',
#     'Case of 12 x 1 lb Jars': '1 lb jar'
#     }