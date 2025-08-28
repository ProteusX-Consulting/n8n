# MongoDB Atlas Setup & Payload CMS Launch

## Step 1: Create MongoDB Atlas Free Tier (2 minutes)

1. **Visit**: https://cloud.mongodb.com/
2. **Sign up** with Google/GitHub or create account
3. **Create Cluster**:
   - Choose "M0 Sandbox" (FREE)
   - Select any cloud provider/region
   - Name: "sean-reed-mcgee" or anything you like
4. **Get Connection String**:
   - Click "Connect" button on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`)

## Step 2: Update Environment Variables

1. **Open**: `.env` file in project root
2. **Replace** the DATABASE_URI with your Atlas connection string:
   ```
   DATABASE_URI=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/sean-reed-mcgee
   ```
3. **Make sure** to replace `your-username` and `your-password` with actual credentials

## Step 3: Migrate Content to Atlas

```bash
npm run migrate:atlas
```

This will:
- ✅ Upload all blog content with full articles
- ✅ Create company portfolio (14 businesses)
- ✅ Upload blog images to media collection
- ✅ Create about page with biography
- ✅ Create admin user for you

## Step 4: Start Payload CMS

```bash
npm run dev
```

## Step 5: Access Admin Panel

- **URL**: http://localhost:3000/admin
- **Email**: admin@seanreedmcgee.com
- **Password**: admin123

## What You'll See:

### Collections Available:
- **Posts** - 9 blog articles with full content
- **Companies** - 14 business portfolio entries  
- **About** - Biographical information
- **Media** - Blog images (Larry Reed McGee photos)
- **Users** - Admin access management

### Content Highlights:
- **Full blog articles** (not excerpts) - complete WordPress content
- **Featured images** for blog posts
- **Company descriptions** for all 14 businesses
- **Complete biography** with family/education details

### Frontend Website:
- **URL**: http://localhost:3000
- **Features**: 
  - Hero section with static profile image
  - Business portfolio with logos/service icons
  - Blog section pulling from CMS
  - Contact information

## Troubleshooting:

### If migration fails:
1. Check Atlas connection string in `.env`
2. Ensure Atlas cluster is running
3. Verify network access (Atlas whitelist IP: 0.0.0.0/0 for development)

### If admin login fails:
- Default credentials: admin@seanreedmcgee.com / admin123
- Reset via Atlas database if needed

🎉 **You'll have the complete Sean Reed McGee website with CMS backend ready to explore!**