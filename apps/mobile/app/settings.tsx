import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useRouter } from "expo-router";
import { theme } from "@/lib/theme";
import { clearToken } from "@/lib/api";

export default function SettingsScreen() {
  const router = useRouter();
  return (
    <View style={s.root}>
      <Text style={s.h1}>Settings</Text>
      <TouchableOpacity
        style={s.row}
        onPress={async () => {
          await clearToken();
          router.replace("/");
        }}
      >
        <Text style={{ color: theme.risk }}>Sign out</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, padding: 16, backgroundColor: theme.bg, gap: 14 },
  h1: { color: theme.text, fontSize: 22, fontWeight: "600" },
  row: {
    backgroundColor: theme.bgCard,
    borderColor: theme.line,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
  },
});
