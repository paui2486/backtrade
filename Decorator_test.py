## S1 ##
# def hello():
#     return 'Hi!'

# def other(func):
#     print('Other code would go here')
#     print(func())

# other(hello)
## S1 ##

## S2 ##
# def decorator_func(func):
    
#     def warpper():
#         print('---begin decorator----')
#         func()
#         print('---end decorator----')
#     return warpper
  

# def to_be_decorated_func():
    
#     print('*********hi*********')

# to_be_decorated_func = decorator_func(to_be_decorated_func)
# to_be_decorated_func()
## S2 ##

## S3 ##
# def decorator_func(func):
    
#     def warpper():
#         print('---begin decorator----')
#         func()
#         print('---end decorator----')
#     return warpper
  
# @decorator_func
# def to_be_decorated_func():
    
#     print('*********hi*********')

# to_be_decorated_func()
## S3 ##

## S4 ##
def decorator__factory_func(func):
    def warpper():
        print('---車廠名稱----')
        func()
        print('---車廠名稱----')
    return warpper

@decorator__factory_func
def KTM():

    print('KTM')

@decorator__factory_func
def Ducati():

    print('DUCATI')

@decorator__factory_func
def Aprilia():

    print('APRILIA')

# KTM()
Ducati()
## S4 ##