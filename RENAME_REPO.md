# 📝 Rename Repository to "policy-analyzer"

## Quick Steps to Rename Your Repository on GitHub:

### 1. Go to Repository Settings
Visit: **https://github.com/Amankum25/pdfextarctor/settings**

### 2. Rename Repository
1. Scroll down to the **"Repository name"** section
2. Change name from: `pdfextarctor`
3. Change to: `policy-analyzer`
4. Click **"Rename"** button

⚠️ GitHub will show a warning - that's normal! Click "I understand, rename this repository"

### 3. Update Local Git Remote

After renaming on GitHub, run these commands locally:

```powershell
# Update the remote URL
git remote set-url origin https://github.com/Amankum25/policy-analyzer.git

# Verify the change
git remote -v
```

### 4. (Optional) Rename Local Folder

```powershell
# Go up one directory
cd ..

# Rename the folder
Rename-Item pdfextarctor policy-analyzer

# Go back into the folder
cd policy-analyzer
```

---

## ✅ What's Already Done:

- ✅ README updated with "Policy Analyzer" title
- ✅ Vercel deployment link added
- ✅ package.json updated to "policy-analyzer"
- ✅ HTML title changed to "Policy Analyzer - Document Q&A"
- ✅ All changes committed and pushed to GitHub

---

## 🔗 Live Links (After Renaming):

- **Repository**: https://github.com/Amankum25/policy-analyzer
- **Live Demo**: https://policy-analyzer-frontend.vercel.app
- **API Docs**: http://localhost:8000/docs (local backend)

---

## 📌 Important Notes:

1. **Old URLs will redirect**: GitHub automatically redirects old repository URLs to the new one
2. **Cloned repos will still work**: Your local repository will work after updating the remote URL
3. **Vercel will still work**: Vercel deployment is not affected by repository rename
4. **Takes ~1 minute**: The rename process is instant on GitHub

---

**Ready? Go to: https://github.com/Amankum25/pdfextarctor/settings and rename to "policy-analyzer"!** 🚀
