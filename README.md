# Fizzbee Website

The hugo markdown for the main fizzbee website

## To run locally
just the static site
```
hugo -D server
```
To make it run along with the playground (local dev only; the frontend's
node app serves `public/`):
```
hugo
cp -R public/ ../frontend/public
```

## To deploy

Build the site and assemble the Firebase Hosting deploy dir in the frontend
checkout (the frontend repo's README documents the checkout location):

```
./deploy.sh <path-to-frontend-checkout>
```

Then deploy from that checkout:

```
firebase deploy --only hosting
```

`deploy.sh` builds into a fresh temp directory on every run (never `./public/`,
which Hugo does not clean) and hands the output to the frontend repo's
`build-hosting.sh`, which assembles the hosting dir from scratch so stale
files from earlier deploys cannot accumulate. The script never deploys by
itself.
