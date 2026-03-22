import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Building2, Mail, MessageSquare, Phone, Send, User } from "lucide-react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { investmentAPI, getCurrentUser, type Opportunity } from "@/services/api";
import { toast } from "sonner";

const investorTypes = ["Individual investor", "Company", "Investment fund", "Government entity", "Other"];
const investmentRanges = ["Below 1M EGP", "1-5M EGP", "5-10M EGP", "10-50M EGP", "More than 50M EGP"];

const ContactPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loadingOpp, setLoadingOpp] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    investorType: "",
    investmentRange: "",
    message: "",
  });

  useEffect(() => {
    const opportunityId = id || "";
    if (!opportunityId) {
      navigate("/investment");
      return;
    }

    investmentAPI
      .getOpportunity(opportunityId)
      .then((response) => setOpportunity(response.data))
      .catch((error: Error) => {
        toast.error(error.message || "Failed to load opportunity");
        navigate("/investment");
      })
      .finally(() => setLoadingOpp(false));
  }, [id, navigate]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const user = getCurrentUser();
    if (!user) {
      toast.error("Please login to express investment interest");
      navigate("/login");
      return;
    }

    if (!id) {
      toast.error("Opportunity ID is missing");
      return;
    }

    setSubmitting(true);
    try {
      await investmentAPI.expressInterest(id, {
        message: formData.message,
        contact_name: formData.name,
        contact_email: formData.email,
        contact_phone: formData.phone,
        company_name: formData.company || undefined,
        investor_type: formData.investorType || undefined,
        budget_range: formData.investmentRange || undefined,
      });
      toast.success("Investment interest sent successfully");
      navigate("/investment/dashboard");
    } catch (error: any) {
      toast.error(error.message || "Failed to send investment interest");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container max-w-2xl px-4">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
            <ArrowRight className="mr-2 h-4 w-4" />
            Back
          </Button>

          <Card className="border-border/50">
            <CardHeader className="pb-2 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <MessageSquare className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-2xl">Investment Contact</CardTitle>
              <p className="text-muted-foreground">
                {loadingOpp ? "Loading opportunity..." : `Send your interest to ${opportunity?.title || "this opportunity"}`}
              </p>
            </CardHeader>

            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="name"
                        placeholder="Enter your name"
                        value={formData.name}
                        onChange={(event) => setFormData({ ...formData, name: event.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number *</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="01xxxxxxxxx"
                        value={formData.phone}
                        onChange={(event) => setFormData({ ...formData, phone: event.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="example@email.com"
                        value={formData.email}
                        onChange={(event) => setFormData({ ...formData, email: event.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company">Company (optional)</Label>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="company"
                        placeholder="Company name"
                        value={formData.company}
                        onChange={(event) => setFormData({ ...formData, company: event.target.value })}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Investor Type</Label>
                    <Select value={formData.investorType} onValueChange={(value) => setFormData({ ...formData, investorType: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose investor type" />
                      </SelectTrigger>
                      <SelectContent>
                        {investorTypes.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Expected Investment Range</Label>
                    <Select value={formData.investmentRange} onValueChange={(value) => setFormData({ ...formData, investmentRange: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose range" />
                      </SelectTrigger>
                      <SelectContent>
                        {investmentRanges.map((range) => (
                          <SelectItem key={range} value={range}>
                            {range}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Message *</Label>
                  <Textarea
                    id="message"
                    placeholder="Describe your interest in this opportunity"
                    value={formData.message}
                    onChange={(event) => setFormData({ ...formData, message: event.target.value })}
                    rows={5}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={submitting || loadingOpp}>
                  <Send className="mr-2 h-5 w-5" />
                  {submitting ? "Sending..." : "Send Interest"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  );
};

export default ContactPage;
