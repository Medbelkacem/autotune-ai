import { Link } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { theme } from "@/lib/theme";

export default function Home() {
  return (
    <View style={s.root}>
      <Text style={s.brand}>
        <Text style={{ color: theme.brand }}>Auto</Text>Tune AI
      </Text>
      <Text style={s.tagline}>
        AI-powered ECU intelligence.{"\n"}Explainable. Safety-bounded. Human-in-the-loop.
      </Text>
      <Link href="/login" asChild>
        <Text style={s.cta}>Sign in →</Text>
      </Link>
      <Link href="/garage" asChild>
        <Text style={s.secondary}>Continue as demo</Text>
      </Link>
    </View>
  );
}

const s = StyleSheet.create({
  root: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    backgroundColor: theme.bg,
    gap: 20,
  },
  brand: { color: theme.text, fontSize: 42, fontWeight: "600" },
  tagline: { color: theme.textMuted, textAlign: "center", lineHeight: 22 },
  cta: {
    backgroundColor: theme.brand,
    color: "#fff",
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    overflow: "hidden",
    fontSize: 16,
  },
  secondary: { color: theme.textMuted, marginTop: 4 },
});
