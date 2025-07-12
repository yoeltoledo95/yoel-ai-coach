# 🚀 Render Deployment Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and create a new repository
2. Name it: `yoel-ai-coach`
3. Make it **Public** (Render works better with public repos)
4. Don't initialize with README (we already have one)

## Step 2: Push to GitHub

```bash
# Add your GitHub repo as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/yoel-ai-coach.git

# Push to GitHub
git push -u origin main
```

## Step 3: Deploy to Render

1. Go to [Render.com](https://render.com)
2. Sign up/Login with your GitHub account
3. Click "New +" → "Web Service"
4. Connect your GitHub account if not already connected
5. Select your `yoel-ai-coach` repository
6. Configure:
   - **Name**: `yoel-ai-coach`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run mobile_logger.py --server.port $PORT --server.address 0.0.0.0`
   - **Plan**: `Free`
7. Click "Create Web Service"

## Step 4: Wait for Deployment

Render will:
- Install dependencies from `requirements.txt`
- Build your Streamlit app
- Deploy to a public URL
- Show you the URL when ready

## Step 5: Access Your App

1. Once deployed, Render will show your app URL
2. It will look like: `https://yoel-ai-coach.onrender.com`
3. Bookmark this URL on your phone!

## Step 6: Test Mobile Access

1. Open the Render URL on your phone
2. Test the Quick Log feature
3. Test the AI Chat
4. Verify data is being saved

## Benefits of Render

✅ **Free tier**: 750 hours/month (way more than you need)  
✅ **Sleep behavior**: Sleeps after 15min, wakes up instantly  
✅ **Auto-deploy**: Updates when you push to GitHub  
✅ **SSL certificate**: Secure HTTPS by default  
✅ **No credit card required**: Truly free  

## Troubleshooting

### If deployment fails:
1. Check Render logs for errors
2. Make sure all files are committed to GitHub
3. Verify `requirements.txt` has all dependencies

### If app doesn't load:
1. Wait a few minutes for deployment to complete
2. Check Render logs for startup errors
3. Make sure the URL is correct

## Next Steps

1. **Test the deployed app** on your phone
2. **Log daily** to build up your data
3. **Customize** the AI responses based on your needs
4. **Add notifications** when ready

Your AI coach will be always accessible at your Render URL! 🎉 