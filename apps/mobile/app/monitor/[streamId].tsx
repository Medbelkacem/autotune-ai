import { useEffect, useState } from "react";
import { useLocalSearchParams } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { theme } from "@/lib/theme";
import { loadToken } from "@/lib/api";
import Constants from "expo-constants";

const CHANNELS = ["rpm", "boost", "afr", "timing", "coolant_temp", "knock"] as const;

export default function MonitorScreen() {
  const { streamId } = useLocalSearchParams<{ streamId: string }>();
  const [values, setValues] = useState<Record<string, number>>({});

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const t = await loadToken();
      const base = (Constants.expoConfig?.extra as any)?.apiUrl?.replace(/^http/, "ws");
      const ws = new WebSocket(`${base}/v1/telemetry/ws/${streamId}?token=${t ?? ""}`);
      ws.onmessage = (e) => {
        if (cancelled) return;
        try {
          const pt = JSON.parse(e.data as string);
          setValues((prev) => ({ ...prev, [pt.channel]: pt.value }));
        } catch {}
      };
      return () => {
        cancelled = true;
        ws.close();
      };
    })();
  }, [streamId]);

  return (
    <View style={s.root}>
      <Text style={s.h1}>Live monitor</Text>
      <View style={s.grid}>
        {CHANNELS.map((c) => (
          <View key={c} style={s.card}>
            <Text style={s.label}>{c}</Text>
            <Text style={s.value}>
              {values[c] != null ? values[c].toFixed(1) : "—"}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, padding: 16, backgroundColor: theme.bg, gap: 14 },
  h1: { color: theme.text, fontSize: 22, fontWeight: "600" },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  card: {
    width: "48%",
    backgroundColor: theme.bgCard,
    borderColor: theme.line,
    borderWidth: 1,
    padding: 14,
    borderRadius: 12,
  },
  label: { color: theme.textMuted, fontSize: 12 },
  value: { color: theme.text, fontSize: 28, fontWeight: "600", marginTop: 4 },
});
