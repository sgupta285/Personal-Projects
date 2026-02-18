import { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { Home } from "./components/pages/Home";
import { HowItWorks } from "./components/pages/HowItWorks";
import { Product } from "./components/pages/Product";
import { Pricing } from "./components/pages/Pricing";
import { About } from "./components/pages/About";
import { FAQ } from "./components/pages/FAQ";
import { Contact } from "./components/pages/Contact";
import { Privacy } from "./components/pages/Privacy";
import { Terms } from "./components/pages/Terms";
import { motion, AnimatePresence } from "motion/react";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");

  // Handle hash-based routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1) || "home";
      setCurrentPage(hash);
    };

    window.addEventListener("hashchange", handleHashChange);
    handleHashChange();

    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (page: string) => {
    window.location.hash = page;
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <Home onNavigate={navigate} />;
      case "how-it-works":
        return <HowItWorks />;
      case "product":
        return <Product />;
      case "pricing":
        return <Pricing onNavigate={navigate} />;
      case "about":
        return <About />;
      case "faq":
        return <FAQ />;
      case "contact":
        return <Contact />;
      case "privacy":
        return <Privacy />;
      case "terms":
        return <Terms />;
      default:
        return <Home onNavigate={navigate} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar currentPage={currentPage} onNavigate={navigate} />
      <main className="flex-1">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>
      <Footer onNavigate={navigate} />
    </div>
  );
}