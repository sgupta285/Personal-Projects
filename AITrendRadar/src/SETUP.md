# 🚀 Trend Radar - Complete Setup Guide

This guide will help you set up and run the Trend Radar website locally on your machine.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

- **Node.js** (version 18 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn** or **pnpm**
- **VS Code** (recommended) - [Download here](https://code.visualstudio.com/)
- **Git** (optional) - [Download here](https://git-scm.com/)

### Check if Node.js is installed:

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
node --version
```

You should see something like `v18.0.0` or higher.

```bash
npm --version
```

You should see a version number like `9.0.0` or higher.

## 📥 Step 1: Get the Project Files

1. Download or clone this project to your computer
2. Extract the files if you downloaded a ZIP
3. Open the project folder in VS Code

### Project Structure

Your folder should look like this:

```
trend-radar/
├── src/
│   ├── components/
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── vite.config.ts
└── ... (other config files)
```

## 🔧 Step 2: Install Dependencies

Open the integrated terminal in VS Code:
- On Mac: Press `Ctrl + `` (backtick) or go to `Terminal > New Terminal`
- On Windows: Press `Ctrl + `` (backtick) or go to `Terminal > New Terminal`

Make sure you're in the project root directory, then run:

```bash
npm install
```

This will download all required packages. It might take a few minutes. You'll see a progress indicator.

### What gets installed?

- React & React DOM
- Vite (build tool)
- Tailwind CSS v4
- Motion (animations)
- All UI components
- TypeScript
- And more...

## ▶️ Step 3: Start the Development Server

Once installation is complete, start the development server:

```bash
npm run dev
```

You should see output like:

```
VITE v6.0.5  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

## 🌐 Step 4: Open in Browser

1. Open your web browser (Chrome, Firefox, Safari, Edge)
2. Go to: **http://localhost:5173**
3. You should see the Trend Radar website!

The page will automatically reload when you save changes to any file.

## 🎨 Step 5: Verify Everything Works

Check that:

- ✅ The dark theme is applied correctly
- ✅ Navigation works (click on different menu items)
- ✅ Page transitions are smooth
- ✅ Buttons and links are clickable
- ✅ The layout is responsive (resize your browser)

## 🛑 Step 6: Stop the Server

When you're done, stop the development server:

- Press `Ctrl + C` in the terminal
- Confirm with `Y` if prompted

## 🏗️ Building for Production

To create an optimized production build:

```bash
npm run build
```

This creates a `dist/` folder with optimized files ready to deploy.

To preview the production build locally:

```bash
npm run preview
```

## 🐛 Troubleshooting

### Port 5173 is already in use

If you see an error about the port being in use:

1. Close any other Vite/development servers
2. Try running `npm run dev` again
3. Or Vite will automatically use a different port (5174, 5175, etc.)

### "Cannot find module" errors

Try deleting `node_modules` and reinstalling:

```bash
rm -rf node_modules package-lock.json
npm install
```

On Windows PowerShell:
```powershell
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install
```

### Styling looks different

1. Make sure `src/styles/globals.css` is imported in `src/main.tsx`
2. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Restart the development server

### TypeScript errors

If you see TypeScript errors but the app runs fine:

1. Make sure all `tsconfig.json` files are present
2. Try restarting VS Code
3. Run `npm run build` to see if there are real errors

### Animations not working

Make sure `motion` is installed:

```bash
npm install motion
```

## 📝 Making Changes

### Edit Content

- Pages are in: `src/components/pages/`
- Components are in: `src/components/`
- Styles are in: `src/styles/globals.css`

### Add New Pages

1. Create a new component in `src/components/pages/`
2. Add a route in `src/App.tsx`
3. Add navigation link in `src/components/Navbar.tsx`

## 🚀 Deployment Options

### Deploy to Vercel (Recommended)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Vercel will auto-detect Vite and deploy

### Deploy to Netlify

1. Push your code to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Import your repository
4. Build command: `npm run build`
5. Publish directory: `dist`

### Deploy to GitHub Pages

1. Install: `npm install --save-dev gh-pages`
2. Add to `package.json` scripts:
   ```json
   "deploy": "vite build && gh-pages -d dist"
   ```
3. Run: `npm run deploy`

## 💡 Tips

- Use VS Code extensions for better development:
  - ES7+ React/Redux/React-Native snippets
  - Tailwind CSS IntelliSense
  - Pretty TypeScript Errors
  - Error Lens

- Hot Module Replacement (HMR) means you see changes instantly without refreshing

- Keep the terminal open while developing to see any errors

## 📞 Need Help?

If you encounter issues:

1. Check the error message in the terminal
2. Check the browser console (F12 > Console tab)
3. Make sure all dependencies are installed
4. Try restarting the dev server
5. Try clearing cache and reinstalling dependencies

## ✅ Success Checklist

- [ ] Node.js installed (v18+)
- [ ] Project files downloaded
- [ ] Dependencies installed (`npm install`)
- [ ] Dev server running (`npm run dev`)
- [ ] Website opens at localhost:5173
- [ ] Dark theme visible
- [ ] Navigation working
- [ ] No console errors

---

**You're all set!** The website should look exactly as designed with the dark theme, smooth animations, and all features working perfectly.

Happy coding! 🎉
