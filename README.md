# Fizzbee Website

The hugo markdown for the main fizzbee website

## To run locally
just the static site
```
hugo -D server
```
To make it run along with the playground
```
hugo
cp -R public/ ../frontend/public
```

## To deploy
Temporary

Copy the public folder to where the nodejs docker image is built.
Then follow the instructions on that page.
Soon, this will be made to be pushed automatically to cloudflare pages
