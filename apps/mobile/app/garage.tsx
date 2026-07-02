import { useEffect, useState } from "react";
import { FlatList, StyleSheet, Text, View, TouchableOpacity } from "react-native";
import { useRouter } from "expo-router";
import { theme } from "@/lib/theme";
import { apiJson } from "@/lib/api";

type Vehicle = { id: string; vin: string; manufacturer: string | null; model: string | null; year: number | null };

export default function GarageScreen() {
  const [items, setItems] = useState<Vehicle[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    apiJson<Vehicle[]>("/vehicles")
      .then(setItems)
      .catch((e) => setErr(String(e)));
  }, []);

  return (
    <View style={s.root}>
      <Text style={s.h1}>Garage</Text>
      {err && <Text style={{ color: theme.risk }}>{err}</Text>}
      <FlatList
        data={items}
        keyExtractor={(v) => v.id}
        contentContainerStyle={{ gap: 10 }}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => router.push(`/vehicle/${item.id}`)} style={s.card}>
            <Text style={{ color: theme.text, fontSize: 16, fontWeight: "600" }}>
              {item.manufacturer} {item.model} {item.year ? `· ${item.year}` : ""}
            </Text>
            <Text style={{ color: theme.textMuted, fontSize: 12, marginTop: 4 }}>
              VIN {"***"}
              {item.vin.slice(-6)}
            </Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={{ color: theme.textMuted }}>No vehicles yet.</Text>}
      />
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, padding: 16, backgroundColor: theme.bg, gap: 12 },
  h1: { color: theme.text, fontSize: 24, fontWeight: "600" },
  card: {
    backgroundColor: theme.bgCard,
    borderColor: theme.line,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
  },
});
