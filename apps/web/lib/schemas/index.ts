import { z } from "zod";

export const Protocol = z.enum([
  "OBD2",
  "KWP2000",
  "UDS",
  "ISO15765-4",
  "DoIP",
  "CAN",
  "CAN_FD",
  "J2534",
]);
export type Protocol = z.infer<typeof Protocol>;

export const EngineSpec = z.object({
  code: z.string(),
  displacement_cc: z.number().int().min(50).max(20_000),
  config: z.string(),
  induction: z.string(),
  cylinders: z.number().int().nullable().optional(),
  valves_per_cylinder: z.number().int().nullable().optional(),
  compression_ratio: z.number().nullable().optional(),
});
export type EngineSpec = z.infer<typeof EngineSpec>;

export const TransmissionSpec = z.object({
  type: z.string(),
  code: z.string().nullable().optional(),
  gears: z.number().int().nullable().optional(),
});
export type TransmissionSpec = z.infer<typeof TransmissionSpec>;

export const EcuSpec = z.object({
  vendor: z.string(),
  model: z.string(),
  hardware_pn: z.string().nullable().optional(),
  software_pn: z.string().nullable().optional(),
  calibration_pn: z.string().nullable().optional(),
  boot_loader: z.string().nullable().optional(),
  firmware_sha256: z.string().length(64).nullable().optional(),
});
export type EcuSpec = z.infer<typeof EcuSpec>;

export const ModificationSignature = z.object({
  detected_signature: z.string(),
  family: z.string().nullable().optional(),
  confidence: z.number().min(0).max(1),
  is_known_tune: z.boolean(),
  is_defeat_device_suspect: z.boolean(),
});
export type ModificationSignature = z.infer<typeof ModificationSignature>;

export const VehicleIdentity = z.object({
  vehicle_identity_id: z.string().uuid(),
  vin: z.string().length(17),
  vin_confidence: z.number().min(0).max(1),
  manufacturer: z.string(),
  model: z.string(),
  model_year: z.number().int(),
  engine: EngineSpec,
  transmission: TransmissionSpec,
  ecu: EcuSpec,
  emission_standard: z.string().nullable().optional(),
  fuel_type: z.string(),
  supported_protocols: z.array(Protocol),
  modification_history: z.array(ModificationSignature),
  detected_at: z.string(),
  signature: z.string().nullable().optional(),
});
export type VehicleIdentity = z.infer<typeof VehicleIdentity>;

export const Domain = z.enum([
  "fuel",
  "ignition",
  "torque_request",
  "throttle",
  "boost",
  "afr_lambda",
  "speed_limiter",
  "rev_limiter",
  "cam_timing",
  "temp_compensation",
  "knock",
  "driver_demand",
  "gear_strategy",
]);
export type Domain = z.infer<typeof Domain>;

export const Citation = z.object({
  source_id: z.string(),
  source_kind: z.string(),
  snippet: z.string().nullable().optional(),
  locator: z.string().nullable().optional(),
  score: z.number().min(0).max(1),
});

export const AnalysisCard = z.object({
  card_id: z.string().uuid(),
  domain: Domain,
  title: z.string(),
  purpose: z.string(),
  inputs: z.array(z.string()),
  outputs: z.array(z.string()),
  relationships: z.array(z.string()),
  observed_summary: z.string(),
  oem_expected_envelope: z.string().nullable().optional(),
  deviation_summary: z.string().nullable().optional(),
  risks: z.array(z.string()),
  optimization_opportunities: z.array(z.string()),
  explanation: z.string(),
  citations: z.array(Citation),
  counter_factuals: z.array(
    z.object({
      if_changed: z.string(),
      then_conclusion_changes: z.string(),
      affected_metrics: z.array(z.string()),
    }),
  ),
  confidence: z.object({
    value: z.number().min(0).max(1),
    calibrated: z.boolean(),
    method: z.string(),
  }),
});
export type AnalysisCard = z.infer<typeof AnalysisCard>;

export const AnalysisReport = z.object({
  report_id: z.string().uuid(),
  vehicle_identity_id: z.string().uuid(),
  calibration_document_id: z.string().uuid(),
  profile_hint: z.string().nullable().optional(),
  cards: z.array(AnalysisCard),
  health_score: z.number().int().min(0).max(100),
  created_at: z.string(),
});
export type AnalysisReport = z.infer<typeof AnalysisReport>;

export const Profile = z.enum([
  "fuel_economy",
  "balanced",
  "performance",
  "track",
  "towing",
  "fleet",
]);
export type Profile = z.infer<typeof Profile>;

export const TelemetryChannel = z.enum([
  "rpm",
  "boost",
  "afr",
  "lambda",
  "timing",
  "coolant_temp",
  "oil_temp",
  "knock",
  "stft",
  "ltft",
  "battery_v",
  "turbo_eff",
  "inj_duty",
  "iat",
  "maf",
  "map",
  "throttle",
  "vehicle_speed",
  "gear",
  "torque_est",
]);
export type TelemetryChannel = z.infer<typeof TelemetryChannel>;

export const TelemetryPoint = z.object({
  stream_id: z.string().uuid(),
  ts: z.string(),
  channel: TelemetryChannel,
  value: z.number(),
});
export type TelemetryPoint = z.infer<typeof TelemetryPoint>;
