/**
 * Hena Wadeena - API Service Layer
 * ==================================
 * Centralized API client for backend communication through the gateway.
 */

type LocationLike = Pick<Location, "protocol" | "hostname" | "port">;

const trimTrailingSlash = (value: string) => value.replace(/\/$/, "");

const normalizeApiBasePath = (value?: string | null) => {
  const trimmed = value?.trim();
  if (!trimmed) return "/api/v1";
  return trimTrailingSlash(trimmed);
};

const isAbsoluteUrl = (value: string) => /^https?:\/\//i.test(value);

const isLocalHost = (hostname: string) => ["localhost", "127.0.0.1", "::1", "[::1]"].includes(hostname);

const resolveApiBaseUrl = (
  configuredBaseUrl = import.meta.env.VITE_API_BASE_URL,
  locationLike: LocationLike | null = typeof window !== "undefined" ? window.location : null,
  isDev = Boolean(import.meta.env.DEV)
) => {
  const baseUrl = normalizeApiBasePath(configuredBaseUrl);

  if (isAbsoluteUrl(baseUrl)) return baseUrl;

  const relativeBase = baseUrl.startsWith("/") ? baseUrl : `/${baseUrl}`;

  if (isDev) return relativeBase;

  // `vite preview` serves the built frontend on :8080 while the gateway runs on :8000.
  // When both are started separately in local production, relative `/api/v1` requests
  // hit the frontend preview server instead of the backend gateway unless we expand them.
  if (locationLike && isLocalHost(locationLike.hostname) && locationLike.port !== "8000") {
    return `${locationLike.protocol}//${locationLike.hostname}:8000${relativeBase}`;
  }

  return relativeBase;
};

const API_BASE_URL = resolveApiBaseUrl();

interface ApiFetchOptions extends RequestInit {
  skipAuth?: boolean;
  retryOnAuthError?: boolean;
  expectNoContent?: boolean;
}

interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  message?: string;
  meta?: Record<string, unknown> | null;
  error?: string | null;
}

let refreshInFlight: Promise<string | null> | null = null;

const parseApiError = (payload: unknown, status: number) => {
  if (typeof payload === "string" && payload.trim()) return payload;

  if (payload && typeof payload === "object") {
    const maybe = payload as Record<string, unknown>;
    if (typeof maybe.detail === "string") return maybe.detail;
    if (Array.isArray(maybe.detail)) {
      const first = maybe.detail[0] as Record<string, unknown> | undefined;
      if (first && typeof first.msg === "string") return first.msg;
      return "Validation error";
    }
    if (typeof maybe.message === "string") return maybe.message;
    if (typeof maybe.error === "string") return maybe.error;
  }

  return `API Error ${status}`;
};

const INVALID_API_RESPONSE_MESSAGE =
  "API request returned HTML instead of JSON. Check VITE_API_BASE_URL or route /api/v1 through the backend gateway.";

const looksLikeHtmlResponse = (raw: string, contentType: string) => {
  const trimmed = raw.trim().toLowerCase();
  return contentType.includes("text/html") || trimmed.startsWith("<!doctype html") || trimmed.startsWith("<html");
};

const toEnvelope = <T>(payload: unknown): ApiEnvelope<T> => {
  if (payload && typeof payload === "object" && "success" in payload && "data" in payload) {
    return payload as ApiEnvelope<T>;
  }

  return { success: true, data: payload as T, meta: null, error: null };
};

const withQuery = (endpoint: string, query?: Record<string, string | number | boolean | undefined | null>) => {
  if (!query) return endpoint;

  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined || v === null || v === "") continue;
    params.set(k, String(v));
  }

  const qs = params.toString();
  return qs ? `${endpoint}?${qs}` : endpoint;
};

const getAppLanguage = (): "ar" | "en" => (localStorage.getItem("app_language") === "en" ? "en" : "ar");

const localizeText = (arabic?: string | null, english?: string | null, fallback = "") => {
  const ar = arabic?.trim();
  const en = english?.trim();
  if (getAppLanguage() === "en") return en || ar || fallback;
  return ar || en || fallback;
};

const fallbackImage = (seed: string, set: "landscape" | "avatar" = "landscape") =>
  set === "avatar"
    ? `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(seed)}`
    : `https://source.unsplash.com/1200x800/?${encodeURIComponent(seed)}`;

const getStoredRefreshToken = () => localStorage.getItem("refresh_token");

const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export interface AuthUser {
  id: string;
  email?: string | null;
  phone?: string | null;
  full_name: string;
  display_name?: string | null;
  avatar_url?: string | null;
  city?: string | null;
  organization?: string | null;
  role: string;
  status: string;
  language: string;
  verified_at?: string | null;
  created_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data: AuthTokens;
}

export const persistAuthSession = (session: AuthTokens) => {
  localStorage.setItem("access_token", session.access_token);
  localStorage.setItem("refresh_token", session.refresh_token);
  localStorage.setItem("user", JSON.stringify(session.user));
};

export const clearAuthSession = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};

export const getCurrentUser = (): AuthUser | null => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
};

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) {
    clearAuthSession();
    return null;
  }

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        clearAuthSession();
        return null;
      }

      const payload = (await res.json()) as AuthResponse;
      if (!payload?.data?.access_token) {
        clearAuthSession();
        return null;
      }

      persistAuthSession(payload.data);
      return payload.data.access_token;
    })().finally(() => {
      refreshInFlight = null;
    });
  }

  return refreshInFlight;
};

async function apiFetch<T>(endpoint: string, options: ApiFetchOptions = {}): Promise<T> {
  const {
    skipAuth = false,
    retryOnAuthError = true,
    expectNoContent = false,
    headers: incomingHeaders,
    body,
    ...rest
  } = options;

  const hasFormData = typeof FormData !== "undefined" && body instanceof FormData;

  const shouldSendJsonContentType = !hasFormData && body !== undefined && body !== null;

  const headers: Record<string, string> = {
    ...(shouldSendJsonContentType ? { "Content-Type": "application/json" } : {}),
    ...(skipAuth ? {} : getAuthHeader()),
    ...((incomingHeaders as Record<string, string> | undefined) || {}),
  };

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...rest,
    body,
    headers,
  });

  const contentType = res.headers.get("content-type")?.toLowerCase() || "";

  if (res.status === 401 && !skipAuth && retryOnAuthError) {
    const renewed = await refreshAccessToken();
    if (renewed) return apiFetch<T>(endpoint, { ...options, retryOnAuthError: false });
  }

  if (!res.ok) {
    const raw = await res.text();
    if (looksLikeHtmlResponse(raw, contentType)) {
      throw new Error(INVALID_API_RESPONSE_MESSAGE);
    }
    let payload: unknown = raw;
    if (raw) {
      try {
        payload = JSON.parse(raw);
      } catch {
        payload = raw;
      }
    }
    throw new Error(parseApiError(payload, res.status));
  }

  if (expectNoContent || res.status === 204) return undefined as T;

  const raw = await res.text();
  if (!raw) return undefined as T;

  if (looksLikeHtmlResponse(raw, contentType)) {
    throw new Error(INVALID_API_RESPONSE_MESSAGE);
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    return raw as unknown as T;
  }
}

export interface LoginRequest {
  email?: string;
  phone?: string;
  password: string;
}

export interface RegisterDocument {
  doc_type: string;
  file_name: string;
  mime_type?: string;
  size_bytes?: number;
}

export interface RegisterRequest {
  email: string;
  phone: string;
  full_name: string;
  password: string;
  role?: string;
  city?: string;
  organization?: string;
  documents?: RegisterDocument[];
}

export interface ProfileUpdateRequest {
  email?: string;
  phone?: string;
  full_name?: string;
  display_name?: string;
  avatar_url?: string;
  city?: string;
  organization?: string;
  language?: "ar" | "en";
}

export const authAPI = {
  login: (body: LoginRequest) =>
    apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
      skipAuth: true,
    }),

  register: (body: RegisterRequest) =>
    apiFetch<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
      skipAuth: true,
    }),

  refresh: (refresh_token: string) =>
    apiFetch<AuthResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
      skipAuth: true,
    }),

  getMe: () => apiFetch<AuthUser>("/auth/me"),

  logout: async () => {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) return { success: true, message: "No active session" };

    return apiFetch<{ success: boolean; message: string }>("/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },
};

export const userAPI = {
  getMe: () => apiFetch<AuthUser>("/users/me"),

  updateMe: (body: ProfileUpdateRequest) =>
    apiFetch<AuthUser>("/users/me", {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  getKyc: () => apiFetch<Array<{ id: string; doc_type: string; doc_url: string; status: string }>>("/users/me/kyc"),
};

export interface Attraction {
  id: string;
  title: string;
  description: string;
  long_description?: string;
  image: string;
  images?: string[];
  rating: number;
  reviews_count?: number;
  duration: string;
  type: string;
  location?: string;
  coordinates?: { lat: number; lng: number };
  featured?: boolean;
  opening_hours?: string;
  ticket_price?: number;
  highlights?: string[];
}

export interface Guide {
  id: string;
  name: string;
  languages: string[];
  specialties: string[];
  rating: number;
  reviews: number;
  price_per_day: number;
  image: string;
  bio?: string;
  available?: boolean;
}

export interface Accommodation {
  id: string;
  title: string;
  type: string;
  price: number;
  price_unit: string;
  rooms: number;
  location: string;
  amenities: string[];
  for_students: boolean;
  image?: string;
  rating?: number;
}

type PoiDto = {
  id: string;
  name_ar: string;
  name_en?: string;
  category: string;
  description?: string;
  address: string;
  lat: number;
  lng: number;
  phone?: string;
  status: string;
  created_at: string;
};

type ListingDto = {
  id: string;
  owner_id: string;
  title: string;
  listing_type: string;
  category: string;
  location: string;
  price: number;
  currency: string;
  description?: string;
  status: string;
  is_verified: boolean;
  created_at: string;
};

const poiToAttraction = (poi: PoiDto, idx: number): Attraction => ({
  id: poi.id,
  title: localizeText(poi.name_ar, poi.name_en, "Attraction"),
  description: poi.description || poi.address,
  long_description: poi.description,
  image: fallbackImage(`attraction-${poi.id}`),
  images: [fallbackImage(`attraction-${poi.id}`)],
  rating: 4.2 + (idx % 6) * 0.1,
  reviews_count: 20 + idx * 7,
  duration: "2-4 hours",
  type: poi.category || "landmark",
  location: poi.address,
  coordinates: { lat: poi.lat, lng: poi.lng },
  featured: idx < 3,
});

const listingToSupplier = (listing: ListingDto, idx: number) => ({
  id: listing.id,
  name: listing.title,
  specialties: [listing.category],
  city: listing.location,
  rating: 4.1 + (idx % 5) * 0.1,
  reviews: 12 + idx * 5,
  verified: listing.is_verified,
  description: listing.description,
  image: fallbackImage(`supplier-${listing.id}`),
  products: [{ name: listing.title, price: listing.price, unit: "item" }],
});

export const tourismAPI = {
  getAttractions: async () => {
    const payload = await apiFetch<ApiEnvelope<PoiDto[]>>("/map/pois");
    const items = toEnvelope<PoiDto[]>(payload).data;
    return { success: true, data: items.map(poiToAttraction) };
  },

  getFeatured: async () => {
    const payload = await tourismAPI.getAttractions();
    return { success: true, data: payload.data.filter((a) => a.featured).slice(0, 3) };
  },

  getAttraction: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<PoiDto>>(`/map/pois/${id}`);
    return { success: true, data: poiToAttraction(toEnvelope<PoiDto>(payload).data, 0) };
  },

  getGuides: async () => {
    const payload = await apiFetch<ApiEnvelope<GuideProfileBackend[]>>("/guides/profiles");
    const guides = toEnvelope<GuideProfileBackend[]>(payload).data.map((g) => ({
      id: g.id,
      name: g.display_name,
      languages: g.languages,
      specialties: g.specialties,
      rating: 4.5,
      reviews: 20,
      price_per_day: g.base_price,
      image: fallbackImage(`guide-${g.user_id}`, "avatar"),
      bio: g.bio,
      available: g.active,
    }));

    return { success: true, data: guides };
  },

  getAccommodations: async () => {
    const payload = await apiFetch<ApiEnvelope<ListingDto[]>>(withQuery("/market/listings", { category: "accommodation" }));
    const listings = toEnvelope<ListingDto[]>(payload).data;
    const data = listings.map((l, idx) => ({
      id: l.id,
      title: l.title,
      type: l.listing_type || "rent",
      price: l.price,
      price_unit: "month",
      rooms: 1 + (idx % 3),
      location: l.location,
      amenities: ["Wi-Fi", "AC"],
      for_students: true,
      image: fallbackImage(`accommodation-${l.id}`),
      rating: 4.1 + (idx % 5) * 0.1,
    }));

    return { success: true, data };
  },
};

export interface PriceItem {
  id: string;
  name: string;
  price: number;
  change: number;
  unit: string;
  category: string;
}

export interface SupplierProduct {
  name: string;
  price: number;
  unit: string;
}

export interface Supplier {
  id: string;
  name: string;
  specialties: string[];
  city: string;
  rating: number;
  reviews: number;
  verified: boolean;
  description?: string;
  phone?: string;
  email?: string;
  image?: string;
  products?: SupplierProduct[];
}

type PriceInsightDto = {
  location: string;
  category: string;
  avg_price: number;
  listings_count: number;
};

export const marketAPI = {
  getPrices: async () => {
    const payload = await apiFetch<ApiEnvelope<PriceInsightDto[]>>("/market/prices/average");
    const insights = toEnvelope<PriceInsightDto[]>(payload).data;

    return {
      success: true,
      data: insights.map((item, idx) => ({
        id: `${item.location}-${item.category}-${idx}`,
        name: `${item.category} (${item.location})`,
        price: item.avg_price,
        change: 0,
        unit: "avg",
        category: item.category,
      })),
    };
  },

  getSuppliers: async () => {
    const payload = await apiFetch<ApiEnvelope<ListingDto[]>>(withQuery("/market/listings", { category: "supplier" }));
    const listings = toEnvelope<ListingDto[]>(payload).data;
    return { success: true, data: listings.map(listingToSupplier) };
  },

  getSupplier: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<ListingDto>>(`/market/listings/${id}`);
    return { success: true, data: listingToSupplier(toEnvelope<ListingDto>(payload).data, 0) };
  },

  createListing: async (body: {
    title: string;
    listing_type: "sell" | "rent" | "land" | "commercial";
    category: string;
    location: string;
    price: number;
    currency?: string;
    description?: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<ListingDto>>("/market/listings", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { success: true, data: toEnvelope<ListingDto>(payload).data };
  },
};

export interface TransportRoute {
  id: string;
  from: string;
  to: string;
  type: string;
  duration: string;
  price: number;
  departures: string[];
  operator: string;
}

export interface Station {
  id: string;
  name: string;
  city: string;
  routes: number;
  address?: string;
  phone?: string;
  facilities?: string[];
  operating_hours?: string;
}

export interface Carpool {
  id: string;
  from: string;
  to: string;
  date: string;
  time: string;
  seats: number;
  price: number;
  driver: string;
  rating: number;
  car_model?: string;
}

type CarpoolRideDto = {
  id: string;
  driver_id: string;
  origin_name: string;
  destination_name: string;
  departure_time: string;
  seats_total: number;
  seats_taken: number;
  price_per_seat: number;
  notes?: string;
  status: string;
  created_at: string;
};

const rideToCarpool = (ride: CarpoolRideDto): Carpool => {
  const dt = new Date(ride.departure_time);
  return {
    id: ride.id,
    from: ride.origin_name,
    to: ride.destination_name,
    date: dt.toISOString().slice(0, 10),
    time: dt.toISOString().slice(11, 16),
    seats: Math.max(ride.seats_total - ride.seats_taken, 0),
    price: ride.price_per_seat,
    driver: `Driver ${ride.driver_id.slice(0, 8)}`,
    rating: 4.4,
    car_model: ride.notes,
  };
};

export const logisticsAPI = {
  getRoutes: async () => {
    const payload = await apiFetch<ApiEnvelope<CarpoolRideDto[]>>("/carpool/rides");
    const rides = toEnvelope<CarpoolRideDto[]>(payload).data;

    return {
      success: true,
      data: rides.map((r) => ({
        id: r.id,
        from: r.origin_name,
        to: r.destination_name,
        type: "carpool",
        duration: "Flexible",
        price: r.price_per_seat,
        departures: [r.departure_time],
        operator: `Driver ${r.driver_id.slice(0, 8)}`,
      })),
    };
  },

  getStations: async () => {
    const payload = await apiFetch<ApiEnvelope<PoiDto[]>>(withQuery("/map/pois", { category: "station" }));
    const stations = toEnvelope<PoiDto[]>(payload).data.map((poi) => ({
      id: poi.id,
      name: localizeText(poi.name_ar, poi.name_en, "Station"),
      city: poi.address,
      routes: 1,
      address: poi.address,
      phone: poi.phone,
      facilities: ["Waiting area"],
      operating_hours: "06:00-22:00",
    }));
    return { success: true, data: stations };
  },

  getStation: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<PoiDto>>(`/map/pois/${id}`);
    const poi = toEnvelope<PoiDto>(payload).data;
    return {
      success: true,
      data: {
        id: poi.id,
        name: localizeText(poi.name_ar, poi.name_en, "Station"),
        city: poi.address,
        routes: 1,
        address: poi.address,
        phone: poi.phone,
        facilities: ["Waiting area"],
        operating_hours: "06:00-22:00",
      } as Station,
    };
  },

  getCarpools: async () => {
    const payload = await apiFetch<ApiEnvelope<CarpoolRideDto[]>>("/carpool/rides");
    return { success: true, data: toEnvelope<CarpoolRideDto[]>(payload).data.map(rideToCarpool) };
  },
};

export interface Opportunity {
  id: string;
  title: string;
  category: string;
  opportunity_type: string;
  location: string;
  investment: string;
  min_investment: number;
  max_investment: number;
  roi: string;
  status: string;
  description: string;
  interest_count: number;
  is_verified: boolean;
  is_watchlisted: boolean;
  created_at: string;
  updated_at: string;
  image?: string;
}

export interface Startup {
  id: string;
  name: string;
  sector: string;
  stage: string;
  location: string;
  team: number;
  description: string;
  funding_needed?: string;
  image?: string;
}

export interface InvestmentInterest {
  id: string;
  opportunity_id: string;
  opportunity_title?: string;
  opportunity_category?: string;
  opportunity_location?: string;
  opportunity_type?: string;
  investor_id: string;
  message: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  company_name?: string;
  investor_type?: string;
  budget_range?: string;
  status: string;
  owner_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface InvestorDashboard {
  status_counts: Record<string, number>;
  recent_interests: InvestmentInterest[];
  watchlist: Opportunity[];
  recommended: Opportunity[];
}

type OpportunityDto = {
  id: string;
  owner_id: string;
  title: string;
  category: string;
  opportunity_type: string;
  location: string;
  min_investment: number;
  max_investment: number;
  investment_range: string;
  expected_roi: string;
  description: string;
  status: string;
  is_verified: boolean;
  interest_count: number;
  is_watchlisted: boolean;
  created_at: string;
  updated_at: string;
};

type InterestDto = {
  id: string;
  opportunity_id: string;
  opportunity_title?: string;
  opportunity_category?: string;
  opportunity_location?: string;
  opportunity_type?: string;
  investor_id: string;
  message: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  company_name?: string;
  investor_type?: string;
  budget_range?: string;
  status: string;
  owner_notes?: string;
  created_at: string;
  updated_at: string;
};

type DashboardDto = {
  status_counts: Record<string, number>;
  recent_interests: InterestDto[];
  watchlist: OpportunityDto[];
  recommended: OpportunityDto[];
};

export interface InterestCreateInput {
  message: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  company_name?: string;
  investor_type?: string;
  budget_range?: string;
}

export interface OpportunityFilters {
  category?: string;
  opportunity_type?: string;
  location?: string;
  owner_id?: string;
  status?: string;
}

const toOpportunity = (o: OpportunityDto): Opportunity => ({
  id: o.id,
  title: o.title,
  category: o.category,
  location: o.location,
  opportunity_type: o.opportunity_type,
  investment: o.investment_range || `${o.min_investment.toLocaleString()} - ${o.max_investment.toLocaleString()} EGP`,
  min_investment: o.min_investment,
  max_investment: o.max_investment,
  roi: o.expected_roi,
  status: o.status,
  description: o.description,
  interest_count: o.interest_count,
  is_verified: o.is_verified,
  is_watchlisted: o.is_watchlisted,
  created_at: o.created_at,
  updated_at: o.updated_at,
  image: fallbackImage(`investment-${o.id}`),
});

const toInterest = (interest: InterestDto): InvestmentInterest => ({
  ...interest,
});

const toDashboard = (dashboard: DashboardDto): InvestorDashboard => ({
  status_counts: dashboard.status_counts || {},
  recent_interests: dashboard.recent_interests.map(toInterest),
  watchlist: dashboard.watchlist.map(toOpportunity),
  recommended: dashboard.recommended.map(toOpportunity),
});

export const investmentAPI = {
  getOpportunities: async (filters: OpportunityFilters = {}) => {
    const payload = await apiFetch<ApiEnvelope<OpportunityDto[]>>(
      withQuery("/investments/opportunities", filters as Record<string, string | number | boolean | undefined | null>),
    );
    return { success: true, data: toEnvelope<OpportunityDto[]>(payload).data.map(toOpportunity) };
  },

  getOpportunity: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<OpportunityDto>>(`/investments/opportunities/${id}`);
    return { success: true, data: toOpportunity(toEnvelope<OpportunityDto>(payload).data) };
  },

  getStartups: async () => {
    const opportunities = (await investmentAPI.getOpportunities({ opportunity_type: "startup" })).data;
    return {
      success: true,
      data: opportunities.map((o, idx) => ({
        id: o.id,
        name: o.title,
        sector: o.category,
        stage: "growth",
        location: o.location,
        team: 5 + idx,
        description: o.description,
        funding_needed: o.investment,
        image: o.image,
      })),
    };
  },

  expressInterest: async (opportunityId: string, body: InterestCreateInput) => {
    const payload = await apiFetch<ApiEnvelope<InterestDto>>(`/investments/opportunities/${opportunityId}/interests`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { success: true, data: toInterest(toEnvelope<InterestDto>(payload).data) };
  },

  getMyInterests: async (status?: string) => {
    const payload = await apiFetch<ApiEnvelope<InterestDto[]>>(withQuery("/investments/interests/my", { status }));
    return { success: true, data: toEnvelope<InterestDto[]>(payload).data.map(toInterest) };
  },

  getWatchlist: async () => {
    const payload = await apiFetch<ApiEnvelope<OpportunityDto[]>>("/investments/watchlist");
    return { success: true, data: toEnvelope<OpportunityDto[]>(payload).data.map(toOpportunity) };
  },

  addWatchlist: async (opportunityId: string) => {
    const payload = await apiFetch<ApiEnvelope<{ id: string; opportunity_id: string }>>(
      `/investments/watchlist/${opportunityId}`,
      { method: "POST" },
    );
    return toEnvelope(payload);
  },

  removeWatchlist: async (opportunityId: string) => {
    await apiFetch<void>(`/investments/watchlist/${opportunityId}`, {
      method: "DELETE",
      expectNoContent: true,
    });
    return { success: true };
  },

  getDashboard: async () => {
    const payload = await apiFetch<ApiEnvelope<DashboardDto>>("/investments/dashboard");
    return { success: true, data: toDashboard(toEnvelope<DashboardDto>(payload).data) };
  },

  createOpportunity: async (body: {
    title: string;
    category: string;
    opportunity_type?: string;
    location: string;
    min_investment: number;
    max_investment: number;
    expected_roi: string;
    description: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<OpportunityDto>>("/investments/opportunities", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { success: true, data: toOpportunity(toEnvelope<OpportunityDto>(payload).data) };
  },
};

export const __investmentTestUtils = {
  toOpportunity,
  toInterest,
  toDashboard,
};

export const __apiTestUtils = {
  resolveApiBaseUrl,
};

export interface POI {
  id: string;
  name_ar: string;
  name_en?: string;
  category: string;
  description: string;
  address: string;
  lat: number;
  lng: number;
  phone?: string;
  rating_avg: number;
  rating_count: number;
  images: string[];
  status: string;
}

export interface CarpoolRide {
  id: string;
  driver_id: string;
  driver_name: string;
  origin_name: string;
  destination_name: string;
  origin: { lat: number; lng: number };
  destination: { lat: number; lng: number };
  departure_time: string;
  seats_total: number;
  seats_taken: number;
  price_per_seat: number;
  notes?: string;
  status: string;
  car_model?: string;
  rating?: number;
}

export const mapAPI = {
  getPOIs: async (category?: string) => {
    const payload = await apiFetch<ApiEnvelope<PoiDto[]>>(withQuery("/map/pois", { category }));
    return {
      success: true,
      data: toEnvelope<PoiDto[]>(payload).data.map((p) => ({
        ...p,
        description: p.description || "",
        rating_avg: 4.4,
        rating_count: 24,
        images: [fallbackImage(`poi-${p.id}`)],
      })) as POI[],
    };
  },

  getPOI: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<PoiDto>>(`/map/pois/${id}`);
    const p = toEnvelope<PoiDto>(payload).data;
    return {
      success: true,
      data: {
        ...p,
        description: p.description || "",
        rating_avg: 4.4,
        rating_count: 24,
        images: [fallbackImage(`poi-${p.id}`)],
      } as POI,
    };
  },

  getCarpoolRides: async () => {
    const payload = await apiFetch<ApiEnvelope<CarpoolRideDto[]>>("/carpool/rides");
    const rides = toEnvelope<CarpoolRideDto[]>(payload).data;
    return {
      success: true,
      data: rides.map((r) => ({
        id: r.id,
        driver_id: r.driver_id,
        driver_name: `Driver ${r.driver_id.slice(0, 8)}`,
        origin_name: r.origin_name,
        destination_name: r.destination_name,
        origin: { lat: 25.45, lng: 30.55 },
        destination: { lat: 27.18, lng: 31.18 },
        departure_time: r.departure_time,
        seats_total: r.seats_total,
        seats_taken: r.seats_taken,
        price_per_seat: r.price_per_seat,
        notes: r.notes,
        status: r.status,
        car_model: r.notes,
        rating: 4.5,
      })) as CarpoolRide[],
    };
  },

  createCarpoolRide: async (body: {
    origin_name: string;
    destination_name: string;
    departure_time: string;
    seats_total: number;
    price_per_seat: number;
    notes?: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<CarpoolRideDto>>("/carpool/rides", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return toEnvelope(payload);
  },

  joinCarpoolRide: async (id: string, seats_requested = 1) => {
    const payload = await apiFetch<ApiEnvelope<CarpoolRideDto>>(`/carpool/rides/${id}/join`, {
      method: "POST",
      body: JSON.stringify({ seats_requested }),
    });
    return toEnvelope(payload);
  },
};

interface GuideProfileBackend {
  id: string;
  user_id: string;
  display_name: string;
  bio: string;
  languages: string[];
  specialties: string[];
  operating_cities?: string[];
  base_price: number;
  active: boolean;
  verified: boolean;
  rating_avg: number;
  rating_count: number;
  total_bookings: number;
  total_earnings?: number;
  created_at: string;
}

interface GuidePackageBackend {
  id: string;
  guide_profile_id: string;
  title: string;
  description: string;
  duration_hrs: number;
  max_people: number;
  price: number;
  category?: string | null;
  includes: string[];
  images: string[];
  active: boolean;
  created_at: string;
}

interface GuideReviewBackend {
  id: string;
  guide_profile_id: string;
  booking_id: string;
  tourist_id: string;
  tourist_name: string;
  rating: number;
  comment: string;
  guide_reply?: string | null;
  created_at: string;
}

export type BookingStatus =
  | "pending"
  | "confirmed"
  | "in_progress"
  | "completed"
  | "cancelled_tourist"
  | "cancelled_guide"
  | "no_show";

export interface GuideProfile {
  id: string;
  user_id: string;
  name: string;
  bio_ar: string;
  languages: string[];
  specialties: string[];
  operating_cities: string[];
  license_number: string;
  license_verified: boolean;
  base_price: number;
  rating_avg: number;
  rating_count: number;
  total_bookings: number;
  total_earnings: number;
  active: boolean;
  image: string;
}

export interface TourPackage {
  id: string;
  guide_id: string;
  title_ar: string;
  description: string;
  duration_hrs: number;
  max_people: number;
  price: number;
  category?: string | null;
  includes: string[];
  images: string[];
  status: string;
}

interface BookingBackend {
  id: string;
  guide_profile_id: string;
  guide_user_id: string;
  guide_display_name?: string;
  tourist_id: string;
  package_id?: string | null;
  package_title?: string | null;
  booking_date: string;
  start_time: string;
  duration_hrs?: number;
  people_count: number;
  total_price: number;
  payment_status?: string;
  notes?: string;
  status: BookingStatus;
  cancellation_actor?: string | null;
  cancelled_reason?: string | null;
  cancellation_refund_percent?: number | null;
  guide_penalty?: boolean;
  cancelled_at?: string | null;
  review_submitted?: boolean;
  created_at: string;
}

export interface Booking {
  id: string;
  package_id?: string;
  guide_id: string;
  guide_user_id: string;
  guide_name: string;
  tourist_id: string;
  package_title: string;
  booking_date: string;
  start_time: string;
  duration_hrs: number;
  people_count: number;
  total_price: number;
  payment_status: string;
  status: BookingStatus;
  notes?: string;
  cancellation_actor?: string | null;
  cancelled_reason?: string | null;
  cancellation_refund_percent?: number | null;
  guide_penalty: boolean;
  cancelled_at?: string | null;
  review_submitted: boolean;
  created_at: string;
}

export interface Review {
  id: string;
  guide_id: string;
  tourist_id: string;
  tourist_name: string;
  rating: number;
  comment: string;
  guide_reply?: string;
  created_at: string;
}

export interface GuideAvailabilitySlot {
  booking_id: string;
  date: string;
  start_time: string;
  end_time: string;
  status: BookingStatus;
}

export interface GuideAvailability {
  guide_profile_id: string;
  month: number;
  year: number;
  blocked_slots: GuideAvailabilitySlot[];
}

const toGuideProfile = (g: GuideProfileBackend): GuideProfile => ({
  id: g.id,
  user_id: g.user_id,
  name: g.display_name,
  bio_ar: g.bio,
  languages: g.languages || [],
  specialties: g.specialties || [],
  operating_cities: g.operating_cities || [],
  license_number: `GUIDE-${(g.user_id || "UNKNOWN").slice(0, 6).toUpperCase()}`,
  license_verified: g.verified,
  base_price: g.base_price,
  rating_avg: Number(g.rating_avg || 0),
  rating_count: Number(g.rating_count || 0),
  total_bookings: Number(g.total_bookings || 0),
  total_earnings: Number(g.total_earnings || 0),
  active: g.active,
  image: fallbackImage(`guide-${g.user_id || g.id}`, "avatar"),
});

const toPackage = (p: GuidePackageBackend): TourPackage => ({
  id: p.id,
  guide_id: p.guide_profile_id,
  title_ar: p.title,
  description: p.description,
  duration_hrs: Number(p.duration_hrs || 0),
  max_people: Number(p.max_people || 1),
  price: Number(p.price || 0),
  category: p.category || null,
  includes: p.includes || [],
  images: p.images?.length ? p.images : [fallbackImage(`guide-package-${p.id}`)],
  status: p.active ? "active" : "inactive",
});

const toReview = (r: GuideReviewBackend): Review => ({
  id: r.id,
  guide_id: r.guide_profile_id,
  tourist_id: r.tourist_id,
  tourist_name: r.tourist_name,
  rating: Number(r.rating || 0),
  comment: r.comment,
  guide_reply: r.guide_reply || undefined,
  created_at: r.created_at,
});

const toBooking = (b: BookingBackend): Booking => ({
  id: b.id,
  package_id: b.package_id || undefined,
  guide_id: b.guide_profile_id,
  guide_user_id: b.guide_user_id,
  guide_name: b.guide_display_name || `Guide ${(b.guide_user_id || "").slice(0, 6)}`,
  tourist_id: b.tourist_id,
  package_title: b.package_title || "Guided Tour",
  booking_date: b.booking_date,
  start_time: b.start_time,
  duration_hrs: Number(b.duration_hrs || 8),
  people_count: b.people_count,
  total_price: b.total_price,
  payment_status: b.payment_status || "unpaid",
  status: b.status,
  notes: b.notes,
  cancellation_actor: b.cancellation_actor || null,
  cancelled_reason: b.cancelled_reason || null,
  cancellation_refund_percent: b.cancellation_refund_percent ?? null,
  guide_penalty: Boolean(b.guide_penalty),
  cancelled_at: b.cancelled_at || null,
  review_submitted: Boolean(b.review_submitted),
  created_at: b.created_at,
});

export const guidesAPI = {
  getGuides: async () => {
    const payload = await apiFetch<ApiEnvelope<GuideProfileBackend[]>>("/guides/profiles");
    return { success: true, data: toEnvelope<GuideProfileBackend[]>(payload).data.map(toGuideProfile) };
  },

  getGuide: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<GuideProfileBackend>>(`/guides/profiles/${id}`);
    return { success: true, data: toGuideProfile(toEnvelope<GuideProfileBackend>(payload).data) };
  },

  getPackages: async (guideId: string, includeInactive = false) => {
    const payload = await apiFetch<ApiEnvelope<GuidePackageBackend[]>>(
      withQuery(`/guides/profiles/${guideId}/packages`, { include_inactive: includeInactive })
    );
    return { success: true, data: toEnvelope<GuidePackageBackend[]>(payload).data.map(toPackage) };
  },

  getReviews: async (guideId: string) => {
    const payload = await apiFetch<ApiEnvelope<GuideReviewBackend[]>>(`/guides/profiles/${guideId}/reviews`);
    return { success: true, data: toEnvelope<GuideReviewBackend[]>(payload).data.map(toReview) };
  },

  getAvailability: async (guideId: string, month: number, year: number) => {
    const payload = await apiFetch<ApiEnvelope<GuideAvailability>>(
      withQuery(`/guides/profiles/${guideId}/availability`, { month, year })
    );
    return { success: true, data: toEnvelope<GuideAvailability>(payload).data };
  },

  createReview: async (bookingId: string, body: { rating: number; comment: string }) => {
    const payload = await apiFetch<ApiEnvelope<GuideReviewBackend>>(`/bookings/${bookingId}/review`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { success: true, data: toReview(toEnvelope<GuideReviewBackend>(payload).data) };
  },

  replyReview: async (reviewId: string, reply: string) => {
    const payload = await apiFetch<ApiEnvelope<GuideReviewBackend>>(`/guides/reviews/${reviewId}/reply`, {
      method: "PATCH",
      body: JSON.stringify({ reply }),
    });
    return { success: true, data: toReview(toEnvelope<GuideReviewBackend>(payload).data) };
  },

  createProfile: async (body: {
    display_name: string;
    bio: string;
    languages?: string[];
    specialties?: string[];
    operating_cities?: string[];
    base_price: number;
  }) => {
    const payload = await apiFetch<ApiEnvelope<GuideProfileBackend>>("/guides/profiles", {
      method: "POST",
      body: JSON.stringify({
        ...body,
        languages: body.languages || [],
        specialties: body.specialties || [],
        operating_cities: body.operating_cities || [],
      }),
    });
    return { success: true, data: toGuideProfile(toEnvelope<GuideProfileBackend>(payload).data) };
  },

  createBooking: async (body: {
    package_id?: string;
    guide_id: string;
    booking_date: string;
    start_time?: string;
    duration_hrs?: number;
    people_count?: number;
    notes?: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>("/bookings", {
      method: "POST",
      body: JSON.stringify({
        guide_profile_id: body.guide_id,
        package_id: body.package_id,
        booking_date: body.booking_date,
        start_time: body.start_time || "09:00",
        duration_hrs: body.duration_hrs,
        people_count: body.people_count || 1,
        notes: body.notes,
      }),
    });

    return { success: true, message: "Booking created", data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  getMyBookings: async (status?: BookingStatus) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend[]>>(withQuery("/guides/bookings/my", { status }));
    return { success: true, data: toEnvelope<BookingBackend[]>(payload).data.map(toBooking) };
  },

  listBookings: async (opts?: { mine_only?: boolean; status?: BookingStatus }) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend[]>>(
      withQuery("/bookings", {
        mine_only: opts?.mine_only ?? true,
        status: opts?.status,
      })
    );
    return { success: true, data: toEnvelope<BookingBackend[]>(payload).data.map(toBooking) };
  },

  updateBookingStatus: async (id: string, status: BookingStatus | "cancelled", reason?: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/bookings/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, reason }),
    });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  confirmBooking: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/guides/bookings/${id}/confirm`, { method: "PATCH" });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  startBooking: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/guides/bookings/${id}/start`, { method: "PATCH" });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  completeBooking: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/guides/bookings/${id}/complete`, { method: "PATCH" });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  markNoShow: async (id: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/guides/bookings/${id}/no-show`, { method: "PATCH" });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },

  cancelBooking: async (id: string, reason?: string) => {
    const payload = await apiFetch<ApiEnvelope<BookingBackend>>(`/guides/bookings/${id}/cancel`, {
      method: "PATCH",
      body: JSON.stringify({ reason }),
    });
    return { success: true, data: toBooking(toEnvelope<BookingBackend>(payload).data) };
  },
};

export interface Wallet {
  id: string;
  user_id: string;
  balance: number;
  currency: string;
  recent_transactions: Transaction[];
}

export interface Transaction {
  id: string;
  type: string;
  amount: number;
  direction: string;
  balance_after: number;
  description: string;
  status: string;
  created_at: string;
  reference_type?: string;
  reference_id?: string;
}

type WalletSummaryDto = {
  user_id: string;
  currency: string;
  balance: number;
  total_credit: number;
  total_debit: number;
};

type TransactionDto = {
  id: string;
  user_id: string;
  tx_type: string;
  direction: string;
  amount: number;
  balance_after: number;
  status: string;
  reference_type?: string;
  reference_id?: string;
  description?: string;
  created_at: string;
};

const toTransaction = (t: TransactionDto): Transaction => ({
  id: t.id,
  type: t.tx_type,
  amount: t.amount,
  direction: t.direction,
  balance_after: t.balance_after,
  description: t.description || t.tx_type,
  status: t.status,
  created_at: t.created_at,
  reference_type: t.reference_type,
  reference_id: t.reference_id,
});

export const paymentsAPI = {
  getWallet: async () => {
    const [summaryPayload, txPayload] = await Promise.all([
      apiFetch<ApiEnvelope<WalletSummaryDto>>("/wallet"),
      apiFetch<ApiEnvelope<TransactionDto[]>>("/payments/transactions"),
    ]);

    const summary = toEnvelope<WalletSummaryDto>(summaryPayload).data;
    const txs = toEnvelope<TransactionDto[]>(txPayload).data.map(toTransaction);

    return {
      success: true,
      data: {
        id: `wallet-${summary.user_id}`,
        user_id: summary.user_id,
        balance: summary.balance,
        currency: summary.currency,
        recent_transactions: txs.slice(0, 5),
      } as Wallet,
    };
  },

  topup: async (body: { amount: number; method?: string }) => {
    const payload = await apiFetch<ApiEnvelope<TransactionDto>>("/wallet/topup", {
      method: "POST",
      body: JSON.stringify(body),
    });

    const tx = toTransaction(toEnvelope<TransactionDto>(payload).data);
    return { success: true, message: "Top-up successful", data: { new_balance: tx.balance_after } };
  },

  getTransactions: async () => {
    const payload = await apiFetch<ApiEnvelope<TransactionDto[]>>("/payments/transactions");
    return { success: true, data: toEnvelope<TransactionDto[]>(payload).data.map(toTransaction) };
  },

  checkout: async (body: { amount: number; reference_type: string; reference_id: string; description?: string }) => {
    const payload = await apiFetch<ApiEnvelope<TransactionDto>>("/payments/checkout", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { success: true, data: toTransaction(toEnvelope<TransactionDto>(payload).data) };
  },
};

export interface Notification {
  id: string;
  type: string;
  title_ar: string;
  body_ar: string;
  data: Record<string, unknown>;
  channel: string[];
  read_at: string | null;
  created_at: string;
}

type NotificationDto = {
  id: string;
  user_id: string;
  type: string;
  title: string;
  body: string;
  channel: string[];
  read_at: string | null;
  status: string;
  created_at: string;
};

export const notificationsAPI = {
  getAll: async () => {
    const payload = await apiFetch<ApiEnvelope<NotificationDto[]>>("/notifications");
    const notifications = toEnvelope<NotificationDto[]>(payload).data.map((n) => ({
      id: n.id,
      type: n.type,
      title_ar: n.title,
      body_ar: n.body,
      data: {},
      channel: n.channel,
      read_at: n.read_at,
      created_at: n.created_at,
    }));

    return { success: true, data: notifications as Notification[] };
  },

  getUnreadCount: async () => {
    const payload = await apiFetch<ApiEnvelope<{ count: number }>>("/notifications/unread-count");
    return toEnvelope<{ count: number }>(payload);
  },

  markRead: async (id: string, read = true) => {
    const payload = await apiFetch<ApiEnvelope<NotificationDto>>(`/notifications/${id}/read`, {
      method: "PATCH",
      body: JSON.stringify({ read }),
    });
    return toEnvelope(payload);
  },

  getPreferences: async () => {
    const payload = await apiFetch<ApiEnvelope<{ notify_push: boolean; notify_email: boolean; notify_sms: boolean }>>(
      "/notifications/preferences"
    );
    return toEnvelope(payload);
  },

  updatePreferences: async (body: { notify_push: boolean; notify_email: boolean; notify_sms: boolean }) => {
    const payload = await apiFetch<ApiEnvelope<{ notify_push: boolean; notify_email: boolean; notify_sms: boolean }>>(
      "/notifications/preferences",
      {
        method: "PUT",
        body: JSON.stringify(body),
      }
    );
    return toEnvelope(payload);
  },
};

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  description: string;
  location: string;
  url: string;
}

type SearchDocumentDto = {
  id: string;
  resource_type: string;
  resource_id: string;
  title: string;
  description: string;
  location?: string;
  tags: string[];
  url?: string;
  score?: number;
  created_at: string;
};

const inferSearchUrl = (doc: SearchDocumentDto): string => {
  if (doc.url) return doc.url;

  switch (doc.resource_type) {
    case "guide":
      return `/guides/${doc.resource_id}`;
    case "supplier":
      return `/marketplace/supplier/${doc.resource_id}`;
    case "investment":
      return `/investment/opportunity/${doc.resource_id}`;
    case "transport":
      return `/logistics/route/${doc.resource_id}`;
    case "poi":
    case "attraction":
      return `/tourism/attraction/${doc.resource_id}`;
    default:
      return "/";
  }
};

export const searchAPI = {
  search: async (q: string, type?: string) => {
    const payload = await apiFetch<ApiEnvelope<SearchDocumentDto[]>>(
      withQuery("/search", {
        q,
        resource_type: type,
      })
    );

    const envelope = toEnvelope<SearchDocumentDto[]>(payload);
    const data = envelope.data.map((doc) => ({
      id: doc.id,
      type: doc.resource_type,
      title: doc.title,
      description: doc.description,
      location: doc.location || "New Valley",
      url: inferSearchUrl(doc),
    }));

    const total = Number((envelope.meta?.total as number | undefined) ?? data.length);
    return { success: true, data, total, query: q };
  },
};

export interface AIChatSource {
  chunk_id: string;
  doc_id: string;
  section_title?: string | null;
  relevance_score: number;
  text_snippet: string;
}

export interface AIChatSessionCreateResponse {
  session_id: string;
  user_id: string | null;
  created_at: string;
  language_preference: string;
  message_count: number;
  is_active: boolean;
  welcome_message: string;
}

export interface AIChatMessageResponse {
  message_id: string;
  session_id: string;
  role: "assistant" | "user";
  content: string;
  language: string;
  created_at: string;
  sources: AIChatSource[];
  domain_relevant: boolean;
  latency_ms?: number | null;
}

export interface AIChatSessionMessage {
  message_id: string;
  role: "assistant" | "user";
  content: string;
  language: string;
  created_at: string;
  sources: AIChatSource[];
}

export interface AIChatSessionViewResponse {
  session_id: string;
  user_id: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  message_count: number;
  messages: AIChatSessionMessage[];
  pagination: {
    page: number;
    per_page: number;
    total_messages: number;
    total_pages: number;
  };
}

export interface AIChatSessionCloseResponse {
  session_id: string;
  closed: boolean;
  message_count: number;
  closed_at: string;
}

export const aiAPI = {
  createSession: async (body?: {
    user_id?: string | null;
    language_preference?: "auto" | "ar" | "en";
    metadata?: Record<string, unknown>;
  }) => {
    const payload = await apiFetch<ApiEnvelope<AIChatSessionCreateResponse>>("/ai/chat/sessions", {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    });
    return toEnvelope<AIChatSessionCreateResponse>(payload);
  },

  sendMessage: async (
    sessionId: string,
    body: {
      content: string;
      language?: "auto" | "ar" | "en";
    }
  ) => {
    const payload = await apiFetch<ApiEnvelope<AIChatMessageResponse>>(
      `/ai/chat/sessions/${encodeURIComponent(sessionId)}/messages`,
      {
        method: "POST",
        body: JSON.stringify(body),
      }
    );
    return toEnvelope<AIChatMessageResponse>(payload);
  },

  getSession: async (sessionId: string, page = 1, perPage = 30) => {
    const payload = await apiFetch<ApiEnvelope<AIChatSessionViewResponse>>(
      withQuery(`/ai/chat/sessions/${encodeURIComponent(sessionId)}`, {
        page,
        per_page: perPage,
      })
    );
    return toEnvelope<AIChatSessionViewResponse>(payload);
  },

  closeSession: async (sessionId: string) => {
    const payload = await apiFetch<ApiEnvelope<AIChatSessionCloseResponse>>(
      `/ai/chat/sessions/${encodeURIComponent(sessionId)}`,
      {
        method: "DELETE",
      }
    );
    return toEnvelope<AIChatSessionCloseResponse>(payload);
  },
};

export interface AdminModerationItem {
  id: string;
  resource_type: string;
  resource_id: string;
  submitted_by: string;
  reason: string;
  status: string;
  reviewer_id?: string | null;
  review_note?: string | null;
  reviewed_at?: string | null;
  subject_title?: string | null;
  subject_category?: string | null;
  source_service?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminUserRow {
  id: string;
  display_name?: string | null;
  email?: string | null;
  role: string;
  is_suspended: boolean;
  is_verified: boolean;
  suspended_reason?: string | null;
  suspended_by?: string | null;
  suspended_at?: string | null;
  unsuspended_by?: string | null;
  unsuspended_at?: string | null;
  verified_by?: string | null;
  verified_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface FeatureFlag {
  key: string;
  enabled: boolean;
  description?: string | null;
  rollout_percentage: number;
  owner_group?: string | null;
  updated_at: string;
}

export interface AdminAuditLog {
  id: string;
  action: string;
  actor_id: string;
  target_type: string;
  target_id: string;
  detail_status?: string | null;
  detail_reason?: string | null;
  detail_note?: string | null;
  detail_queue_id?: string | null;
  created_at: string;
}

export interface AdminAnnouncement {
  id: string;
  title: string;
  body: string;
  audience: string;
  status: string;
  priority: string;
  created_by: string;
  starts_at?: string | null;
  ends_at?: string | null;
  created_at: string;
  updated_at: string;
}

export const adminAPI = {
  getModerationQueue: async (params?: { status?: string; page?: number; page_size?: number; resource_type?: string }) => {
    const payload = await apiFetch<ApiEnvelope<AdminModerationItem[]>>(
      withQuery("/admin/moderation", {
        status: params?.status,
        page: params?.page,
        page_size: params?.page_size,
        resource_type: params?.resource_type,
      })
    );
    return toEnvelope<AdminModerationItem[]>(payload);
  },

  reviewModerationItem: async (id: string, status: "approved" | "rejected", note?: string) => {
    const payload = await apiFetch<ApiEnvelope<AdminModerationItem>>(`/admin/moderation/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status, note }),
    });
    return toEnvelope<AdminModerationItem>(payload);
  },

  reportContent: async (body: {
    resource_type: string;
    resource_id: string;
    reason: string;
    subject_title?: string;
    subject_category?: string;
    source_service?: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<AdminModerationItem>>("/admin/report", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return toEnvelope<AdminModerationItem>(payload);
  },

  getUsers: async (params?: { page?: number; page_size?: number; role?: string; search?: string }) => {
    const payload = await apiFetch<ApiEnvelope<AdminUserRow[]>>(
      withQuery("/admin/users", {
        page: params?.page,
        page_size: params?.page_size,
        role: params?.role,
        search: params?.search,
      })
    );
    return toEnvelope<AdminUserRow[]>(payload);
  },

  suspendUser: async (userId: string, reason?: string) => {
    const payload = await apiFetch<ApiEnvelope<AdminUserRow>>(`/admin/users/${userId}/suspend`, {
      method: "PATCH",
      body: JSON.stringify({ reason }),
    });
    return toEnvelope<AdminUserRow>(payload);
  },

  unsuspendUser: async (userId: string) => {
    const payload = await apiFetch<ApiEnvelope<AdminUserRow>>(`/admin/users/${userId}/unsuspend`, {
      method: "PATCH",
    });
    return toEnvelope<AdminUserRow>(payload);
  },

  verifyUser: async (userId: string) => {
    const payload = await apiFetch<ApiEnvelope<AdminUserRow>>(`/admin/users/${userId}/verify`, {
      method: "PATCH",
    });
    return toEnvelope<AdminUserRow>(payload);
  },

  getFlags: async () => {
    const payload = await apiFetch<ApiEnvelope<FeatureFlag[]>>("/admin/flags");
    return toEnvelope<FeatureFlag[]>(payload);
  },

  updateFlag: async (
    key: string,
    body: { enabled: boolean; description?: string; rollout_percentage?: number; owner_group?: string }
  ) => {
    const payload = await apiFetch<ApiEnvelope<FeatureFlag>>(`/admin/flags/${encodeURIComponent(key)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    return toEnvelope<FeatureFlag>(payload);
  },

  getAuditLog: async (params?: { page?: number; page_size?: number; action?: string }) => {
    const payload = await apiFetch<ApiEnvelope<AdminAuditLog[]>>(
      withQuery("/admin/audit-log", {
        page: params?.page,
        page_size: params?.page_size,
        action: params?.action,
      })
    );
    return toEnvelope<AdminAuditLog[]>(payload);
  },

  getAnnouncements: async (params?: { page?: number; page_size?: number }) => {
    const payload = await apiFetch<ApiEnvelope<AdminAnnouncement[]>>(
      withQuery("/admin/announcements", {
        page: params?.page,
        page_size: params?.page_size,
      })
    );
    return toEnvelope<AdminAnnouncement[]>(payload);
  },

  getActiveAnnouncements: async (params?: { page?: number; page_size?: number }) => {
    const payload = await apiFetch<ApiEnvelope<AdminAnnouncement[]>>(
      withQuery("/admin/announcements/active", {
        page: params?.page,
        page_size: params?.page_size,
      }),
      { skipAuth: true }
    );
    return toEnvelope<AdminAnnouncement[]>(payload);
  },

  createAnnouncement: async (body: {
    title: string;
    body: string;
    audience?: string;
    status?: "active" | "inactive" | "scheduled";
    priority?: "low" | "normal" | "high" | "urgent";
    starts_at?: string;
    ends_at?: string;
  }) => {
    const payload = await apiFetch<ApiEnvelope<AdminAnnouncement>>("/admin/announcements", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return toEnvelope<AdminAnnouncement>(payload);
  },

  updateAnnouncement: async (
    id: string,
    body: {
      title?: string;
      body?: string;
      audience?: string;
      status?: "active" | "inactive" | "scheduled";
      priority?: "low" | "normal" | "high" | "urgent";
      starts_at?: string;
      ends_at?: string;
    }
  ) => {
    const payload = await apiFetch<ApiEnvelope<AdminAnnouncement>>(`/admin/announcements/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    return toEnvelope<AdminAnnouncement>(payload);
  },

  deleteAnnouncement: async (id: string) =>
    apiFetch<void>(`/admin/announcements/${id}`, {
      method: "DELETE",
      expectNoContent: true,
    }),
};

export interface AnalyticsOverview {
  date_from: string;
  date_to: string;
  total_events: number;
  users: { active_users: number; new_users: number };
  listings: { created: number; updated: number; verified: number };
  bookings: { requested: number; completed: number; cancelled: number };
  revenue: { total_amount: number };
}

export interface AnalyticsKpis {
  date_from: string;
  date_to: string;
  active_users: number;
  new_users: number;
  booking_completion_rate: number;
  booking_confirmation_rate: number;
  search_share: number;
  revenue_total: number;
}

export const analyticsAPI = {
  getOverview: async (params?: { date_from?: string; date_to?: string }) => {
    const payload = await apiFetch<ApiEnvelope<AnalyticsOverview>>(
      withQuery("/analytics/overview", {
        date_from: params?.date_from,
        date_to: params?.date_to,
      })
    );
    return toEnvelope<AnalyticsOverview>(payload);
  },

  getKpis: async (params?: { date_from?: string; date_to?: string }) => {
    const payload = await apiFetch<ApiEnvelope<AnalyticsKpis>>(
      withQuery("/analytics/kpis", {
        date_from: params?.date_from,
        date_to: params?.date_to,
      })
    );
    return toEnvelope<AnalyticsKpis>(payload);
  },
};


