-- 20260220_001_supplier_facility_refactor.sql
-- Purpose: add company-level metadata, create facility-centric matching schema,
-- and migrate legacy supplier operational columns into facilities.

BEGIN;

-- Base suppliers table (safe create for new environments)
CREATE TABLE IF NOT EXISTS public.suppliers (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT NOT NULL DEFAULT '',
  star_rating NUMERIC(2,1) NOT NULL DEFAULT 0,
  capacity TEXT DEFAULT '',
  certifications TEXT[] DEFAULT '{}',
  inbound_capabilities TEXT[] DEFAULT '{}',
  outbound_capabilities TEXT[] DEFAULT '{}',
  special_handling TEXT[] DEFAULT '{}',
  description TEXT DEFAULT '',
  contact_email TEXT DEFAULT '',
  contact_phone TEXT DEFAULT '',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Extend suppliers with operational fields (legacy compatibility)
ALTER TABLE public.suppliers
  ADD COLUMN IF NOT EXISTS service_type TEXT DEFAULT 'warehouse',
  ADD COLUMN IF NOT EXISTS volume_pattern TEXT DEFAULT 'steady',
  ADD COLUMN IF NOT EXISTS term_type TEXT DEFAULT 'long_term',
  ADD COLUMN IF NOT EXISTS vas_services TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS dock_type TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS entry_type TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS equipment_present TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS access_barriers TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS temperature_range_min NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS temperature_range_max NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS is_food_grade BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_hazmat BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS security_level TEXT DEFAULT 'standard',
  ADD COLUMN IF NOT EXISTS integration_methods TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS total_reviews INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS on_time_rate NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS claim_rate NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS damage_rate NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS max_sqft NUMERIC DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS min_order_volume INTEGER DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS max_order_volume INTEGER DEFAULT NULL;

-- Company-level fields
ALTER TABLE public.suppliers
  ADD COLUMN IF NOT EXISTS industry text,
  ADD COLUMN IF NOT EXISTS website text,
  ADD COLUMN IF NOT EXISTS employee_count integer,
  ADD COLUMN IF NOT EXISTS currency text,
  ADD COLUMN IF NOT EXISTS country text,
  ADD COLUMN IF NOT EXISTS headquarters_address text,
  ADD COLUMN IF NOT EXISTS review_comments text;

-- Facilities (search entity)
CREATE TABLE IF NOT EXISTS public.facilities (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  supplier_id uuid NOT NULL REFERENCES public.suppliers(id) ON DELETE CASCADE,
  facility_name text NOT NULL,
  facility_type text DEFAULT 'warehouse',
  address text,
  city text,
  state text,
  country text,
  zip_code text,
  size text,
  utilization text,
  capabilities text[] DEFAULT '{}',
  dot_number text,
  mc_number text,
  safer text,
  location text NOT NULL DEFAULT '',
  capacity text DEFAULT '',
  inbound_capabilities text[] DEFAULT '{}',
  outbound_capabilities text[] DEFAULT '{}',
  certifications text[] DEFAULT '{}',
  special_handling text[] DEFAULT '{}',
  service_type text DEFAULT 'warehouse',
  temperature_range_min numeric,
  temperature_range_max numeric,
  is_food_grade boolean DEFAULT false,
  is_hazmat boolean DEFAULT false,
  max_sqft numeric,
  dock_type text,
  entry_type text,
  equipment_present text[] DEFAULT '{}',
  access_barriers text[] DEFAULT '{}',
  security_level text DEFAULT 'standard',
  vas_services text[] DEFAULT '{}',
  volume_pattern text DEFAULT 'steady',
  term_type text DEFAULT 'long_term',
  integration_methods text[] DEFAULT '{}',
  on_time_rate numeric,
  claim_rate numeric,
  damage_rate numeric,
  min_order_volume integer,
  max_order_volume integer,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.facilities ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read facilities" ON public.facilities;
DROP POLICY IF EXISTS "Public insert facilities" ON public.facilities;
DROP POLICY IF EXISTS "Public update facilities" ON public.facilities;
DROP POLICY IF EXISTS "Public delete facilities" ON public.facilities;
CREATE POLICY "Public read facilities" ON public.facilities FOR SELECT USING (true);
CREATE POLICY "Public insert facilities" ON public.facilities FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update facilities" ON public.facilities FOR UPDATE USING (true);
CREATE POLICY "Public delete facilities" ON public.facilities FOR DELETE USING (true);

DROP TRIGGER IF EXISTS update_facilities_updated_at ON public.facilities;
CREATE TRIGGER update_facilities_updated_at
  BEFORE UPDATE ON public.facilities
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Vehicles
CREATE TABLE IF NOT EXISTS public.vehicles (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  supplier_id uuid NOT NULL REFERENCES public.suppliers(id) ON DELETE CASCADE,
  vehicle_name text,
  vehicle_type text,
  vehicle_number text,
  vehicle_capacity text,
  insurance_certificate text,
  fitness_certificate text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.vehicles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read vehicles" ON public.vehicles;
DROP POLICY IF EXISTS "Public insert vehicles" ON public.vehicles;
DROP POLICY IF EXISTS "Public update vehicles" ON public.vehicles;
DROP POLICY IF EXISTS "Public delete vehicles" ON public.vehicles;
CREATE POLICY "Public read vehicles" ON public.vehicles FOR SELECT USING (true);
CREATE POLICY "Public insert vehicles" ON public.vehicles FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update vehicles" ON public.vehicles FOR UPDATE USING (true);
CREATE POLICY "Public delete vehicles" ON public.vehicles FOR DELETE USING (true);
DROP TRIGGER IF EXISTS update_vehicles_updated_at ON public.vehicles;
CREATE TRIGGER update_vehicles_updated_at
  BEFORE UPDATE ON public.vehicles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Agents
CREATE TABLE IF NOT EXISTS public.agents (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  supplier_id uuid NOT NULL REFERENCES public.suppliers(id) ON DELETE CASCADE,
  agent_name text,
  agent_code text,
  agent_phone text,
  agent_vehicle_type text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read agents" ON public.agents;
DROP POLICY IF EXISTS "Public insert agents" ON public.agents;
DROP POLICY IF EXISTS "Public update agents" ON public.agents;
DROP POLICY IF EXISTS "Public delete agents" ON public.agents;
CREATE POLICY "Public read agents" ON public.agents FOR SELECT USING (true);
CREATE POLICY "Public insert agents" ON public.agents FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update agents" ON public.agents FOR UPDATE USING (true);
CREATE POLICY "Public delete agents" ON public.agents FOR DELETE USING (true);
DROP TRIGGER IF EXISTS update_agents_updated_at ON public.agents;
CREATE TRIGGER update_agents_updated_at
  BEFORE UPDATE ON public.agents
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Loads
CREATE TABLE IF NOT EXISTS public.loads (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  supplier_id uuid NOT NULL REFERENCES public.suppliers(id) ON DELETE CASCADE,
  load_ref text,
  customer_name text,
  customer_phone text,
  delivery_address text,
  delivery_pincode text,
  order_value numeric,
  order_type text,
  cargo_type text,
  vehicle_type text,
  status text,
  shipment_number text,
  expected_delivery_time timestamptz,
  actual_delivery_time timestamptz,
  budget numeric,
  billing_status text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.loads ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read loads" ON public.loads;
DROP POLICY IF EXISTS "Public insert loads" ON public.loads;
DROP POLICY IF EXISTS "Public update loads" ON public.loads;
DROP POLICY IF EXISTS "Public delete loads" ON public.loads;
CREATE POLICY "Public read loads" ON public.loads FOR SELECT USING (true);
CREATE POLICY "Public insert loads" ON public.loads FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update loads" ON public.loads FOR UPDATE USING (true);
CREATE POLICY "Public delete loads" ON public.loads FOR DELETE USING (true);
DROP TRIGGER IF EXISTS update_loads_updated_at ON public.loads;
CREATE TRIGGER update_loads_updated_at
  BEFORE UPDATE ON public.loads
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Migrate legacy supplier operational data to facilities, one row per supplier if not already migrated.
INSERT INTO public.facilities (
  supplier_id, facility_name, location, capacity, inbound_capabilities, outbound_capabilities,
  certifications, special_handling, service_type, temperature_range_min, temperature_range_max,
  is_food_grade, is_hazmat, max_sqft, dock_type, entry_type, equipment_present, access_barriers,
  security_level, vas_services, volume_pattern, term_type, integration_methods,
  on_time_rate, claim_rate, damage_rate, min_order_volume, max_order_volume, facility_type
)
SELECT
  s.id, s.name, s.location, s.capacity, s.inbound_capabilities, s.outbound_capabilities,
  s.certifications, s.special_handling, s.service_type, s.temperature_range_min, s.temperature_range_max,
  s.is_food_grade, s.is_hazmat, s.max_sqft, s.dock_type, s.entry_type, s.equipment_present, s.access_barriers,
  s.security_level, s.vas_services, s.volume_pattern, s.term_type, s.integration_methods,
  s.on_time_rate, s.claim_rate, s.damage_rate, s.min_order_volume, s.max_order_volume, s.service_type
FROM public.suppliers s
WHERE NOT EXISTS (
  SELECT 1 FROM public.facilities f WHERE f.supplier_id = s.id
);

-- Optional clean-up after successful migration to facility-centric model
ALTER TABLE public.suppliers
  DROP COLUMN IF EXISTS location,
  DROP COLUMN IF EXISTS capacity,
  DROP COLUMN IF EXISTS inbound_capabilities,
  DROP COLUMN IF EXISTS outbound_capabilities,
  DROP COLUMN IF EXISTS certifications,
  DROP COLUMN IF EXISTS special_handling,
  DROP COLUMN IF EXISTS service_type,
  DROP COLUMN IF EXISTS temperature_range_min,
  DROP COLUMN IF EXISTS temperature_range_max,
  DROP COLUMN IF EXISTS is_food_grade,
  DROP COLUMN IF EXISTS is_hazmat,
  DROP COLUMN IF EXISTS max_sqft,
  DROP COLUMN IF EXISTS dock_type,
  DROP COLUMN IF EXISTS entry_type,
  DROP COLUMN IF EXISTS equipment_present,
  DROP COLUMN IF EXISTS access_barriers,
  DROP COLUMN IF EXISTS security_level,
  DROP COLUMN IF EXISTS vas_services,
  DROP COLUMN IF EXISTS volume_pattern,
  DROP COLUMN IF EXISTS term_type,
  DROP COLUMN IF EXISTS integration_methods,
  DROP COLUMN IF EXISTS on_time_rate,
  DROP COLUMN IF EXISTS claim_rate,
  DROP COLUMN IF EXISTS damage_rate,
  DROP COLUMN IF EXISTS min_order_volume,
  DROP COLUMN IF EXISTS max_order_volume;

COMMIT;
