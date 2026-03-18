import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { useNavigate } from "react-router-dom";
import { Car, Calendar, Clock, Users, DollarSign, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { mapAPI, getCurrentUser } from "@/services/api";
import { toast } from "sonner";

const cities = ["Kharga", "Dakhla", "Farafra", "Paris", "Cairo", "Assiut", "Luxor", "Bahariya"];

const CreateTripPage = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    date: "",
    time: "",
    seats: "",
    price: "",
    notes: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const user = getCurrentUser();
    if (!user) {
      toast.error("Please login to post a trip");
      navigate("/login");
      return;
    }

    if (formData.from === formData.to) {
      toast.error("Origin and destination must be different");
      return;
    }

    setSubmitting(true);
    try {
      const departure = new Date(`${formData.date}T${formData.time}:00`);
      if (Number.isNaN(departure.getTime())) {
        throw new Error("Invalid departure date/time");
      }

      await mapAPI.createCarpoolRide({
        origin_name: formData.from,
        destination_name: formData.to,
        departure_time: departure.toISOString(),
        seats_total: Number(formData.seats),
        price_per_seat: Number(formData.price),
        notes: formData.notes || undefined,
      });

      toast.success("Trip posted successfully");
      navigate("/logistics");
    } catch (err: any) {
      toast.error(err.message || "Failed to create trip");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <section className="py-8 md:py-12">
        <div className="container px-4 max-w-2xl">
          <Button variant="ghost" onClick={() => navigate("/logistics")} className="mb-6">
            <ArrowRight className="h-4 w-4 mr-2" />
            Back to Logistics
          </Button>

          <Card className="border-border/50">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Car className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-2xl">Post a New Carpool Trip</CardTitle>
              <p className="text-muted-foreground">Create a ride so nearby users can join your trip.</p>
            </CardHeader>

            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="from">From</Label>
                    <Select value={formData.from} onValueChange={(value) => setFormData({ ...formData, from: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose departure city" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city} value={city}>
                            {city}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="to">To</Label>
                    <Select value={formData.to} onValueChange={(value) => setFormData({ ...formData, to: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose destination city" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city} value={city}>
                            {city}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
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

                  <div className="space-y-2">
                    <Label htmlFor="time">Time</Label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="time"
                        type="time"
                        value={formData.time}
                        onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="seats">Available Seats</Label>
                    <div className="relative">
                      <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="seats"
                        type="number"
                        min="1"
                        max="12"
                        placeholder="3"
                        value={formData.seats}
                        onChange={(e) => setFormData({ ...formData, seats: e.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="price">Price per Seat (EGP)</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="price"
                        type="number"
                        min="0"
                        placeholder="150"
                        value={formData.price}
                        onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Trip Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Pickup hints, luggage notes, or any details for passengers"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                  />
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={submitting}>
                  <Car className="h-5 w-5 mr-2" />
                  {submitting ? "Posting..." : "Publish Trip"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </Layout>
  );
};

export default CreateTripPage;
