# Dr.Griffin ReadMe

## Document address
List of all methods whit parameter and example. here

`url: http://127.0.0.1:8000/api/v1/redoc/`

## Swagger address
List of all methods in swagger mode (test methods).

`url: http://127.0.0.1:8000/api/v1/swagger/`

### Registration steps:
1. (step 1) http://drgriffin.ir/api/v1/user/signup/
   
`{
    "phone_number": "09120000000",
    "password": "123456"
}`

2. (step 2) http://drgriffin.ir/api/v1/user/verify-user/

`{
    "phone_number": "09120000000",
    "generated_token": "259733"
}`

resend SMS: http://drgriffin.ir/api/v1/user/resend/

`{
    "phone_number": "09120000000"
}`

### Forget Password Steps:
1. (step 1) http://drgriffin.ir/api/v1/user/forget-password-token/
   
`{
    "phone_number": "09120000000"
}`


2. (step 2) http://drgriffin.ir/api/v1/user/forget-password-verify/

`{
    "phone_number": "09120141318",
    "generated_token": "245452",
    "password": "dar1abed2"
}`

### Change Password:
http://drgriffin.ir/api/v1/user/change-password/

_Need Bearer Token_

`{
    "old_password": "*123#456",
    "new_password": "*123/456"
}`

### run mysql docker
> https://medium.com/@minghz42/docker-setup-for-django-on-mysql-1f063c9d16a0

#### persist volume
> https://stackoverflow.com/questions/65345516/docker-permission-denied-to-local-mysql-volume
> https://stackoverflow.com/questions/39175194/docker-compose-persistent-data-mysql

### php/myAdmin
> https://towardsdatascience.com/how-to-run-mysql-and-phpmyadmin-using-docker-17dfe107eab7
> 
