# MaxMind GeoIP Setup for Wazuh

## Step 1: Register for MaxMind Account (FREE)

1. Go to: https://www.maxmind.com/en/geolite2/signup
2. Create a free account
3. Verify your email
4. Log in to your MaxMind account
5. Go to: Account → My License Key
6. Click "Generate new license key"
7. Copy your License Key (you'll need this)

## Step 2: Download GeoLite2 Database

Once you have your license key, we'll download the GeoIP database to Wazuh.

The database file needed is: **GeoLite2-City.mmdb**

## Step 3: Configure Wazuh

We need to:
1. Place the database on the Wazuh manager
2. Configure the Wazuh decoder to use it
3. Restart Wazuh manager
4. Re-process alerts with GeoIP enrichment

## Step 4: Create Visualizations

Once enriched, we can create:
- World map of attack origins
- Country distribution chart
- Geographic heatmap

---

## NEXT STEPS

You need to:
1. Get your MaxMind License Key
2. Come back with it so we can automate the download and setup

Then I'll handle all the Wazuh configuration automatically.

