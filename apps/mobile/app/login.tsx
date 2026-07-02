import { useState } from "react";
import { useRouter } from "expo-router";
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";
import { theme } from "@/lib/theme";
import { apiFetch, saveToken } from "@/lib/api";

export default function LoginScreen() {
  const [email, setEmail] = useState("owner@demo.autotune.ai");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function submit() {
    setBusy(true);
    setErr(null);
    try {
      const r = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (!r.ok) throw new Error((await r.json()).detail ?? "login failed");
      const tokens = await r.json();
      await saveToken(tokens.access_token);
      router.replace("/garage");
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={s.root}>
      <Text style={s.title}>Sign in</Text>
      <TextInput
        style={s.input}
        placeholder="Email"
        placeholderTextColor={theme.textMuted}
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={s.input}
        placeholder="Password"
        placeholderTextColor={theme.textMuted}
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      {err && <Text style={{ color: theme.risk }}>{err}</Text>}
      <TouchableOpacity style={s.btn} onPress={submit} disabled={busy}>
        <Text style={s.btnText}>{busy ? "Signing in…" : "Continue →"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, padding: 24, gap: 12, backgroundColor: theme.bg, justifyContent: "center" },
  title: { color: theme.text, fontSize: 28, fontWeight: "600", marginBottom: 12 },
  input: {
    backgroundColor: theme.bgSoft,
    borderColor: theme.line,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    color: theme.text,
  },
  btn: { backgroundColor: theme.brand, padding: 14, borderRadius: 12, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "600" },
});
