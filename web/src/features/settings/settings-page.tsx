import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import {
  SegmentedControl,
  SegmentedControlItem,
} from "@/components/ui/segmented-control";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { AppSettings } from "@/types/api";
import { getHealth, getSettings, updateSettings } from "./settings-api";

function useSettingsMutation() {
  return useMutation({
    mutationFn: (settings: Partial<AppSettings>) => updateSettings(settings),
    onSuccess: () => {
      toast.success("Settings saved");
    },
    onError: () => {
      toast.error("Failed to save settings");
    },
  });
}

function GeneralTab({ settings }: { settings: AppSettings }) {
  const [theme, setTheme] = useState(settings.theme ?? "system");
  const [language, setLanguage] = useState(settings.language ?? "en");
  const mutation = useSettingsMutation();

  const handleSave = () => {
    mutation.mutate({ theme, language });
  };

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <span className="text-sm font-medium">Theme</span>
        <SegmentedControl
          type="single"
          value={theme}
          onValueChange={(v) => {
            if (v) setTheme(v as "light" | "dark" | "system");
          }}
        >
          <SegmentedControlItem value="light">Light</SegmentedControlItem>
          <SegmentedControlItem value="dark">Dark</SegmentedControlItem>
          <SegmentedControlItem value="system">System</SegmentedControlItem>
        </SegmentedControl>
      </div>

      <div className="space-y-2">
        <label htmlFor="language-select" className="text-sm font-medium">
          Language
        </label>
        <Select value={language} onValueChange={setLanguage}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="zh">中文</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button onClick={handleSave} disabled={mutation.isPending}>
        {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
        <Save className="h-4 w-4" />
        Save
      </Button>
    </div>
  );
}

function LLMTab({ settings }: { settings: AppSettings }) {
  const [model, setModel] = useState(settings.llm_model ?? "");
  const [apiKey, setApiKey] = useState("");
  const mutation = useSettingsMutation();

  const handleSave = () => {
    const payload: Partial<AppSettings> = { llm_model: model };
    if (apiKey) payload.api_key = apiKey;
    mutation.mutate(payload);
    setApiKey("");
  };

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <label htmlFor="llm-model" className="text-sm font-medium">
          Model
        </label>
        <Input
          id="llm-model"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <label htmlFor="llm-api-key" className="text-sm font-medium">
            API Key
          </label>
          <Badge variant={settings.api_key_set ? "outline" : "destructive"}>
            {settings.api_key_set ? "已设置" : "未设置"}
          </Badge>
        </div>
        <Input
          id="llm-api-key"
          type="password"
          placeholder="Enter new API key..."
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
      </div>

      <Button onClick={handleSave} disabled={mutation.isPending}>
        {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
        <Save className="h-4 w-4" />
        Save
      </Button>
    </div>
  );
}

function VaultTab({ settings }: { settings: AppSettings }) {
  const [vaultPath, setVaultPath] = useState(settings.vault_path ?? "");
  const mutation = useSettingsMutation();

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 10000,
  });

  const handleSave = () => {
    mutation.mutate({ vault_path: vaultPath });
  };

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <label htmlFor="vault-path" className="text-sm font-medium">
          Vault Path
        </label>
        <div className="flex gap-2">
          <Input
            id="vault-path"
            value={vaultPath}
            onChange={(e) => setVaultPath(e.target.value)}
            className="flex-1"
          />
          <Button variant="outline" disabled>
            Browse
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <span className="text-sm font-medium">Connection Status</span>
        <div className="flex items-center gap-2">
          <div
            className={`h-2.5 w-2.5 rounded-full ${
              health?.vault_connected ? "bg-green-600" : "bg-red-600"
            }`}
          />
          <span className="text-sm text-muted-foreground">
            {health?.vault_connected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      <Button onClick={handleSave} disabled={mutation.isPending}>
        {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
        <Save className="h-4 w-4" />
        Save
      </Button>
    </div>
  );
}

function AdvancedTab({ settings }: { settings: AppSettings }) {
  const [apiUrl, setApiUrl] = useState(settings.api_url ?? "");
  const [cacheEnabled, setCacheEnabled] = useState(
    (settings.cache_enabled as boolean) ?? true,
  );
  const [logLevel, setLogLevel] = useState(
    (settings.log_level as string) ?? "INFO",
  );
  const mutation = useSettingsMutation();

  const handleSave = () => {
    mutation.mutate({
      api_url: apiUrl,
      cache_enabled: cacheEnabled,
      log_level: logLevel,
    });
  };

  return (
    <div className="max-w-lg space-y-6">
      <div className="space-y-2">
        <label htmlFor="api-url" className="text-sm font-medium">
          API URL
        </label>
        <Input
          id="api-url"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
        />
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="cache-enabled"
          checked={cacheEnabled}
          onCheckedChange={(v) => setCacheEnabled(v === true)}
        />
        <label htmlFor="cache-enabled" className="text-sm font-medium">
          Cache Enabled
        </label>
      </div>

      <div className="space-y-2">
        <label htmlFor="log-level" className="text-sm font-medium">
          Log Level
        </label>
        <Select value={logLevel} onValueChange={setLogLevel}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="DEBUG">DEBUG</SelectItem>
            <SelectItem value="INFO">INFO</SelectItem>
            <SelectItem value="WARNING">WARNING</SelectItem>
            <SelectItem value="ERROR">ERROR</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button onClick={handleSave} disabled={mutation.isPending}>
        {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
        <Save className="h-4 w-4" />
        Save
      </Button>
    </div>
  );
}

export function SettingsPage() {
  const {
    data: settings,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !settings) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3">
        <p className="text-sm text-muted-foreground">
          Failed to load settings.
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-4 p-4 md:p-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Tabs defaultValue="general" className="flex-1">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="llm">LLM</TabsTrigger>
          <TabsTrigger value="vault">Vault</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-4">
          <GeneralTab settings={settings} />
        </TabsContent>

        <TabsContent value="llm" className="mt-4">
          <LLMTab settings={settings} />
        </TabsContent>

        <TabsContent value="vault" className="mt-4">
          <VaultTab settings={settings} />
        </TabsContent>

        <TabsContent value="advanced" className="mt-4">
          <AdvancedTab settings={settings} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
