# GitHub Pages Deployment Guide

## Prerequisites

1. Ensure Git is installed
2. Ensure you have a GitHub account
3. Ensure you have created a GitHub repository

## Deployment Steps

### 1. Initialize Local Repository

```bash
# Open terminal/command prompt in project directory
git init

# Add all files to staging area
git add .

# Commit files
git commit -m "Initial commit: Research portfolio website"
```

### 2. Connect to GitHub Repository

```bash
# Add remote repository (replace with your username and repository name)
git remote add origin https://github.com/syydaniel/yiyangshen.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### 3. Enable GitHub Pages

1. Log in to GitHub
2. Go to your repository page
3. Click on "Settings" tab
4. Find "Pages" in the left menu
5. In "Source" section, select "Deploy from a branch"
6. Select "main" branch
7. Select "/ (root)" folder
8. Click "Save"

### 4. Access Your Website

After deployment, your website will be available at:
`https://syydaniel.github.io/yiyangshen/`

## Update Website

After making code changes, use the following commands to update the website:

```bash
# Add modified files
git add .

# Commit changes
git commit -m "Update website content"

# Push to GitHub
git push origin main
```

## Custom Domain (Optional)

If you want to use a custom domain:

1. Create a `CNAME` file in the repository root
2. Write your domain name in the file (e.g., `yourdomain.com`)
3. Set up CNAME record with your domain provider pointing to `syydaniel.github.io`

## Troubleshooting

### If Git command is not available
- Windows: Download and install [Git for Windows](https://git-scm.com/download/win)
- Mac: Use `brew install git` or download from official website
- Linux: Use package manager to install `git`

### If push fails
- Check network connection
- Verify GitHub credentials are correct
- Try using SSH keys instead of HTTPS

### If website doesn't display
- Wait a few minutes for GitHub Pages deployment to complete
- Check Pages configuration in repository settings
- Check the Actions tab in the repository for any errors

## File Structure

Ensure your repository contains the following files:
```
yiyangshen/
├── index.html
├── styles.css
├── script.js
├── README.md
└── DEPLOYMENT.md
```

## Technical Support

If you encounter issues, you can:
1. Check GitHub Pages documentation
2. Check browser console for errors
3. Validate HTML/CSS syntax
