import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ChatWidget } from "@/components/ai/ChatWidget";
import Index from "./pages/Index";
import LogisticsPage from "./pages/LogisticsPage";
import MarketplacePage from "./pages/MarketplacePage";
import InvestmentPage from "./pages/InvestmentPage";
import TourismPage from "./pages/TourismPage";
import NotFound from "./pages/NotFound";

// Auth pages
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";

// Profile pages
import ProfilePage from "./pages/profile/ProfilePage";
import WalletPage from "./pages/profile/WalletPage";
import BookingsPage from "./pages/profile/BookingsPage";
import NotificationsPage from "./pages/profile/NotificationsPage";

// Guides pages
import GuidesPage from "./pages/guides/GuidesPage";
import GuideProfilePage from "./pages/guides/GuideProfilePage";


// Logistics pages
import CreateTripPage from "./pages/logistics/CreateTripPage";
import BookTripPage from "./pages/logistics/BookTripPage";
import RouteDetailsPage from "./pages/logistics/RouteDetailsPage";
import StationDetailsPage from "./pages/logistics/StationDetailsPage";

// Marketplace pages
import PricesPage from "./pages/marketplace/PricesPage";
import SupplierDetailsPage from "./pages/marketplace/SupplierDetailsPage";

// Investment pages
import OpportunityDetailsPage from "./pages/investment/OpportunityDetailsPage";
import ContactPage from "./pages/investment/ContactPage";
import SearchResultsPage from "./pages/search/SearchResultsPage";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import ReviewerDashboardPage from "./pages/admin/ReviewerDashboardPage";
import ModeratorDashboardPage from "./pages/admin/ModeratorDashboardPage";

// Tourism pages
import GuideBookingPage from "./pages/tourism/GuideBookingPage";
import AccommodationDetailsPage from "./pages/tourism/AccommodationDetailsPage";
import AttractionsPage from "./pages/tourism/AttractionsPage";
import AttractionDetailsPage from "./pages/tourism/AttractionDetailsPage";
import AccommodationInquiryPage from "./pages/tourism/AccommodationInquiryPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          {/* Auth */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          {/* Profile / User Dashboard */}
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/wallet" element={<WalletPage />} />
          <Route path="/bookings" element={<BookingsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          {/* Guides */}
          <Route path="/guides" element={<GuidesPage />} />
          <Route path="/guides/:id" element={<GuideProfilePage />} />
          {/* Search */}
          <Route path="/search" element={<SearchResultsPage />} />
          {/* Tourism */}
          <Route path="/tourism" element={<TourismPage />} />
          <Route path="/tourism/attractions" element={<AttractionsPage />} />
          <Route path="/tourism/attraction/:id" element={<AttractionDetailsPage />} />
          <Route path="/tourism/guide-booking/:id" element={<GuideBookingPage />} />
          <Route path="/tourism/accommodation/:id" element={<AccommodationDetailsPage />} />
          <Route path="/tourism/accommodation-inquiry/:id" element={<AccommodationInquiryPage />} />
          {/* Logistics */}
          <Route path="/logistics" element={<LogisticsPage />} />
          <Route path="/logistics/create-trip" element={<CreateTripPage />} />
          <Route path="/logistics/book/:id" element={<BookTripPage />} />
          <Route path="/logistics/route/:id" element={<RouteDetailsPage />} />
          <Route path="/logistics/:id" element={<RouteDetailsPage />} />
          <Route path="/logistics/station/:id" element={<StationDetailsPage />} />
          <Route path="/book-trip/:id" element={<BookTripPage />} />
          {/* Marketplace */}
          <Route path="/marketplace" element={<MarketplacePage />} />
          <Route path="/marketplace/prices" element={<PricesPage />} />
          <Route path="/marketplace/supplier/:id" element={<SupplierDetailsPage />} />
          {/* Investment */}
          <Route path="/investment" element={<InvestmentPage />} />
          <Route path="/investment/opportunity/:id" element={<OpportunityDetailsPage />} />
          <Route path="/investment/contact/:id" element={<ContactPage />} />
          {/* Admin / Reviewer */}
          <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
          <Route path="/reviewer/dashboard" element={<ReviewerDashboardPage />} />
          <Route path="/moderator/dashboard" element={<ModeratorDashboardPage />} />
          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
        {/* AI Chatbot Widget â€” visible on all pages */}
        <ChatWidget />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;







