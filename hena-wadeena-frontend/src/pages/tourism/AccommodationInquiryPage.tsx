import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowRight, User, Phone, Mail, Calendar, Users, MessageSquare, Send, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { adminAPI, getCurrentUser } from "@/services/api";
import { toast } from "sonner";

const tenantTypes = ["University student", "Government employee", "Private-sector employee", "Family", "Other"];

const AccommodationInquiryPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    tenantType: "",
    moveInDate: "",
    duration: "",
    occupants: "",
    isStudent: false,
    university: "",
    message: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const user = getCurrentUser();
    if (!user) {
      toast.error("Please login to submit reservation request");
      navigate("/login");
      return;
    }

    const listingId = id || "unknown-listing";

    const reasonLines = [
      `Accommodation reservation inquiry from ${formData.name}.`,
      `Phone: ${formData.phone}`,
      formData.email ? `Email: ${formData.email}` : "",
      formData.tenantType ? `Tenant type: ${formData.tenantType}` : "",
      formData.moveInDate ? `Move-in: ${formData.moveInDate}` : "",
      formData.duration ? `Duration: ${formData.duration}` : "",
      formData.occupants ? `Occupants: ${formData.occupants}` : "",
      formData.isStudent ? `Student: yes${formData.university ? ` (${formData.university})` : ""}` : "Student: no",
      formData.message ? `Message: ${formData.message}` : "",
    ].filter(Boolean);

    setSubmitting(true);
    try {
      await adminAPI.reportContent({
        resource_type: "accommodation_listing",
        resource_id: listingId,
        reason: reasonLines.join("\n"),
        subject_title: `Accommodation inquiry for listing ${listingId}`,
        subject_category: "accommodation",
        source_service: "market-service",
      });

      toast.success("Reservation request sent successfully");
      navigate("/tourism");
    } catch (err: any) {
      toast.error(err.message || "Failed to send reservation request");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container px-4 max-w-2xl">
          <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
            <ArrowRight className="h-4 w-4 mr-2" />
            Back
          </Button>

          <Card className="border-border/50">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <MessageSquare className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-2xl">Accommodation Reservation Request</CardTitle>
              <p className="text-muted-foreground">Submit your request and the owner/moderation team will follow up.</p>
            </CardHeader>

            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="name"
                        placeholder="Enter your name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number *</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="01xxxxxxxxx"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="example@email.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Tenant Type *</Label>
                  <Select value={formData.tenantType} onValueChange={(value) => setFormData({ ...formData, tenantType: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose tenant type" />
                    </SelectTrigger>
                    <SelectContent>
                      {tenantTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="isStudent"
                    checked={formData.isStudent}
                    onCheckedChange={(checked) => setFormData({ ...formData, isStudent: checked as boolean })}
                  />
                  <Label htmlFor="isStudent" className="flex items-center gap-2 cursor-pointer">
                    <GraduationCap className="h-4 w-4 text-primary" />
                    I am a university student
                  </Label>
                </div>

                {formData.isStudent && (
                  <div className="space-y-2">
                    <Label htmlFor="university">University / Faculty</Label>
                    <Input
                      id="university"
                      placeholder="New Valley University - Faculty of Engineering"
                      value={formData.university}
                      onChange={(e) => setFormData({ ...formData, university: e.target.value })}
                    />
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="moveInDate">Expected Move-in Date</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="moveInDate"
                        type="date"
                        value={formData.moveInDate}
                        onChange={(e) => setFormData({ ...formData, moveInDate: e.target.value })}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="duration">Expected Rent Duration</Label>
                    <Select value={formData.duration} onValueChange={(value) => setFormData({ ...formData, duration: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose duration" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1-3">1-3 months</SelectItem>
                        <SelectItem value="3-6">3-6 months</SelectItem>
                        <SelectItem value="6-12">6-12 months</SelectItem>
                        <SelectItem value="12+">More than 12 months</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="occupants">Number of Occupants</Label>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="occupants"
                      type="number"
                      min="1"
                      placeholder="Number of occupants"
                      value={formData.occupants}
                      onChange={(e) => setFormData({ ...formData, occupants: e.target.value })}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Message</Label>
                  <Textarea
                    id="message"
                    placeholder="Any specific requirements or notes"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    rows={4}
                  />
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={submitting}>
                  <Send className="h-5 w-5 mr-2" />
                  {submitting ? "Sending..." : "Send Reservation Request"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  );
};

export default AccommodationInquiryPage;
