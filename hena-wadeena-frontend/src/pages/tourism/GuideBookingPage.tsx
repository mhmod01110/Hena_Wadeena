import { useEffect, useMemo, useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Calendar, Users, Star, MapPin, Check, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { guidesAPI, getCurrentUser, type GuideProfile } from "@/services/api";
import { toast } from "sonner";

const GuideBookingPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [step, setStep] = useState(1);
  const [loadingGuide, setLoadingGuide] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [guide, setGuide] = useState<GuideProfile | null>(null);

  const [formData, setFormData] = useState({
    date: "",
    days: 1,
    groupSize: 1,
    name: "",
    phone: "",
    email: "",
    notes: "",
  });

  useEffect(() => {
    const gid = id || "";
    if (!gid) {
      navigate("/guides");
      return;
    }

    guidesAPI
      .getGuide(gid)
      .then((res) => setGuide(res.data))
      .catch((err: any) => {
        toast.error(err.message || "Failed to load guide profile");
        navigate("/guides");
      })
      .finally(() => setLoadingGuide(false));
  }, [id, navigate]);

  const totalPrice = useMemo(() => {
    const base = guide?.base_price || 0;
    return base * formData.days * formData.groupSize;
  }, [guide?.base_price, formData.days, formData.groupSize]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (step === 1) {
      setStep(2);
      return;
    }

    const user = getCurrentUser();
    if (!user) {
      toast.error("Please login before booking a guide");
      navigate("/login");
      return;
    }

    if (!guide) {
      toast.error("Guide profile is not loaded");
      return;
    }

    setSubmitting(true);
    try {
      await guidesAPI.createBooking({
        guide_id: guide.id,
        booking_date: formData.date,
        start_time: "09:00",
        people_count: formData.groupSize,
        notes: [
          `Requested days: ${formData.days}`,
          `Booker name: ${formData.name}`,
          `Phone: ${formData.phone}`,
          formData.email ? `Email: ${formData.email}` : "",
          formData.notes ? `Notes: ${formData.notes}` : "",
        ]
          .filter(Boolean)
          .join("\n"),
      });

      toast.success("Guide booking request created successfully");
      navigate("/bookings");
    } catch (err: any) {
      toast.error(err.message || "Failed to create guide booking");
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingGuide) {
    return (
      <Layout>
        <section className="py-10">
          <div className="container px-4 max-w-3xl">
            <p className="text-muted-foreground">Loading guide profile...</p>
          </div>
        </section>
      </Layout>
    );
  }

  if (!guide) {
    return null;
  }

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container px-4 max-w-3xl">
          <Button variant="ghost" onClick={() => (step === 1 ? navigate("/tourism") : setStep(1))} className="mb-6">
            <ArrowRight className="h-4 w-4 mr-2" />
            {step === 1 ? "Back to Guides" : "Back to Step 1"}
          </Button>

          <div className="flex items-center justify-center gap-4 mb-8">
            <div className="flex items-center gap-2">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= 1 ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                {step > 1 ? <Check className="h-4 w-4" /> : "1"}
              </div>
              <span className="text-sm font-medium">Trip Details</span>
            </div>
            <div className="h-px w-8 bg-border" />
            <div className="flex items-center gap-2">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= 2 ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                2
              </div>
              <span className="text-sm font-medium">Booking Info</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="border-border/50 lg:order-2">
              <CardContent className="p-6">
                <div className="flex items-center gap-4 mb-4">
                  <img src={guide.image} alt={guide.name} className="h-16 w-16 rounded-full object-cover" />
                  <div>
                    <h3 className="font-semibold text-lg">{guide.name}</h3>
                    <div className="flex items-center gap-1 text-accent-foreground">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="font-medium">{guide.rating_avg}</span>
                      <span className="text-sm text-muted-foreground">({guide.rating_count} reviews)</span>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-4">{guide.bio_ar}</p>

                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Languages className="h-4 w-4 text-primary" />
                    <span>{guide.languages.join(", ") || "Arabic"}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-primary" />
                    <span>{guide.specialties.join(", ") || "Local tours"}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Price per day</span>
                    <span className="text-xl font-bold text-primary">{guide.base_price} EGP</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50 lg:col-span-2 lg:order-1">
              <CardHeader>
                <CardTitle className="text-xl">{step === 1 ? "Trip Details" : "Booking Information"}</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {step === 1 ? (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="date">Trip Start Date</Label>
                        <div className="relative">
                          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="date"
                            type="date"
                            value={formData.date}
                            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                            className="pl-10"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Number of Days</Label>
                          <div className="flex items-center gap-4">
                            <Button type="button" variant="outline" size="icon" onClick={() => setFormData({ ...formData, days: Math.max(1, formData.days - 1) })}>-</Button>
                            <span className="text-xl font-bold w-8 text-center">{formData.days}</span>
                            <Button type="button" variant="outline" size="icon" onClick={() => setFormData({ ...formData, days: formData.days + 1 })}>+</Button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label>Group Size</Label>
                          <div className="flex items-center gap-4">
                            <Button type="button" variant="outline" size="icon" onClick={() => setFormData({ ...formData, groupSize: Math.max(1, formData.groupSize - 1) })}>-</Button>
                            <span className="text-xl font-bold w-8 text-center">{formData.groupSize}</span>
                            <Button type="button" variant="outline" size="icon" onClick={() => setFormData({ ...formData, groupSize: formData.groupSize + 1 })}>+</Button>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="notes">Trip Notes</Label>
                        <Textarea
                          id="notes"
                          placeholder="Tell the guide about your trip preferences"
                          value={formData.notes}
                          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                          rows={3}
                        />
                      </div>

                      <div className="bg-primary/5 rounded-lg p-4 flex items-center justify-between">
                        <span className="text-muted-foreground">Estimated Total</span>
                        <span className="text-2xl font-bold text-primary">{totalPrice} EGP</span>
                      </div>

                      <Button type="button" className="w-full" size="lg" onClick={() => setStep(2)}>
                        Continue
                      </Button>
                    </>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="name">Full Name</Label>
                        <Input id="name" placeholder="Enter your full name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="phone">Phone</Label>
                          <Input id="phone" type="tel" placeholder="01xxxxxxxxx" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} required />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="email">Email</Label>
                          <Input id="email" type="email" placeholder="example@email.com" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                        </div>
                      </div>

                      <div className="bg-muted/50 rounded-lg p-4 space-y-2">
                        <h4 className="font-semibold mb-3">Booking Summary</h4>
                        <div className="flex justify-between text-sm"><span className="text-muted-foreground">Guide</span><span>{guide.name}</span></div>
                        <div className="flex justify-between text-sm"><span className="text-muted-foreground">Date</span><span>{formData.date}</span></div>
                        <div className="flex justify-between text-sm"><span className="text-muted-foreground">Duration</span><span>{formData.days} days</span></div>
                        <div className="flex justify-between text-sm"><span className="text-muted-foreground">People</span><span>{formData.groupSize}</span></div>
                        <div className="flex justify-between font-semibold pt-2 border-t border-border"><span>Total</span><span className="text-primary">{totalPrice} EGP</span></div>
                      </div>

                      <Button type="submit" className="w-full" size="lg" disabled={submitting}>
                        {submitting ? "Submitting..." : "Confirm Booking"}
                      </Button>
                    </>
                  )}
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default GuideBookingPage;
