import { Layout } from "@/components/layout/Layout";
import { HeroSection } from "@/components/home/HeroSection";
import { QuickAccess } from "@/components/home/QuickAccess";
import { MissionCards } from "@/components/home/MissionCards";
import { FeaturedSection } from "@/components/home/FeaturedSection";
import { PriceSnapshot } from "@/components/home/PriceSnapshot";

const Index = () => {
  return (
    <Layout>
      <HeroSection />
      <QuickAccess />
      <MissionCards />
      <FeaturedSection />
      <PriceSnapshot />
    </Layout>
  );
};

export default Index;

