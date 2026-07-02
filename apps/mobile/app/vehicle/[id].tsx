import { useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { theme } from "@/lib/theme";
import { apiFetch } from "@/lib/api";

export default function VehicleScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [scanId, setScanId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function startScan() {
    setBusy(true);
    try {
      const r = await apiFetch("/scans", {
        method: "POST",
        body: JSON.stringify({ vehicle_id: id }),
      });
      if (r.ok) {
        const j = await r.json();
        setScanId(j.id);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={s.root}>
      <Text style={s.h1}>Vehicle</Text>
      <View style={s.card}>
        <Text style={{ color: theme.text, fontSize: 18 }}>Bosch MED17.5.20</Text>
        <Text style={{ color: theme.textMuted, marginTop: 4 }}>SW-PN 8K2907115AF_0010</Text>
      </View>

      <TouchableOpacity style={s.btnPrimary} onPress={startScan} disabled={busy}>
        <Text style={s.btnPrimaryText}>{busy ? "Starting…" : "Start scan"}</Text>
      </TouchableOpacity>

      {scanId && (
        <View style={s.card}>
          <Text style={{ color: theme.text }}>Scan queued</Text>
          <Text style={{ color: theme.textMuted, marginTop: 4 }}>{scanId}</Text>
        </View>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, padding: 16, gap: 14, backgroundColor: theme.bg },
  h1: { color: theme.text, fontSize: 24, fontWeight: "600" },
  card: {
    backgroundColor: theme.bgCard,
    borderColor: theme.line,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
  },
  btnPrimary: { backgroundColor: theme.brand, padding: 14, borderRadius: 12, alignItems: "center" },
  btnPrimaryText: { color: "#fff", fontWeight: "600" },
});
