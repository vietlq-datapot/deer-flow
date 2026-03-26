"use client";

import {
  BotIcon,
  CheckCircle2Icon,
  EyeIcon,
  EyeOffIcon,
  KeyRoundIcon,
  Loader2Icon,
  SaveIcon,
  SearchIcon,
  XCircleIcon,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useAdminConfig, useSaveAdminConfig } from "@/core/admin/hooks";
import { useI18n } from "@/core/i18n/hooks";
import { cn } from "@/lib/utils";

import { SettingsSection } from "./settings-section";

// ── Key field component ──────────────────────────────────────────────────────

interface KeyFieldProps {
  label: string;
  description: string;
  placeholder: string;
  isSet: boolean;
  hint: string;
  value: string;
  onChange: (v: string) => void;
  icon: React.ReactNode;
  required?: boolean;
}

function KeyField({
  label,
  description,
  placeholder,
  isSet,
  hint,
  value,
  onChange,
  icon,
  required,
}: KeyFieldProps) {
  const [show, setShow] = useState(false);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-2 text-sm font-medium">
          {icon}
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
        {isSet ? (
          <Badge
            variant="outline"
            className="gap-1 border-green-500 text-green-600 dark:text-green-400"
          >
            <CheckCircle2Icon className="size-3" />
            Đã cấu hình
          </Badge>
        ) : (
          <Badge variant="outline" className="gap-1 border-orange-400 text-orange-500">
            <XCircleIcon className="size-3" />
            Chưa cấu hình
          </Badge>
        )}
      </div>
      <p className="text-muted-foreground text-xs">{description}</p>
      <div className="relative">
        <Input
          type={show ? "text" : "password"}
          placeholder={isSet ? `${hint} (để trống = giữ nguyên)` : placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pr-10 font-mono text-sm"
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          className="text-muted-foreground hover:text-foreground absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
          tabIndex={-1}
        >
          {show ? <EyeOffIcon className="size-4" /> : <EyeIcon className="size-4" />}
        </button>
      </div>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────

export function AdminSettingsPage() {
  const { t } = useI18n();
  const { data: config, isLoading, isError } = useAdminConfig();
  const { mutateAsync: saveConfig, isPending } = useSaveAdminConfig();

  const [deepseekKey, setDeepseekKey] = useState("");
  const [telegramToken, setTelegramToken] = useState("");
  const [tavilyKey, setTavilyKey] = useState("");

  const handleSave = async () => {
    const update: Record<string, string> = {};
    if (deepseekKey.trim()) update.deepseek_api_key = deepseekKey.trim();
    if (telegramToken.trim()) update.telegram_bot_token = telegramToken.trim();
    if (tavilyKey.trim()) update.tavily_api_key = tavilyKey.trim();

    if (Object.keys(update).length === 0) {
      toast.info("Không có thay đổi nào để lưu.");
      return;
    }

    try {
      await saveConfig(update);
      setDeepseekKey("");
      setTelegramToken("");
      setTavilyKey("");
      toast.success("Cấu hình đã được lưu thành công! Khởi động lại server để áp dụng.");
    } catch (err) {
      toast.error(`Lỗi: ${err instanceof Error ? err.message : "Không thể lưu cấu hình."}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2Icon className="text-muted-foreground size-6 animate-spin" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-destructive rounded-lg border border-red-200 bg-red-50 p-4 text-sm dark:border-red-900 dark:bg-red-950">
        Không thể kết nối tới backend. Hãy đảm bảo server đang chạy.
      </div>
    );
  }

  const allRequiredSet = config?.deepseek_api_key_set && config?.telegram_bot_token_set;

  return (
    <div className="space-y-8">
      {/* Status banner */}
      <div
        className={cn(
          "flex items-start gap-3 rounded-lg border p-4",
          allRequiredSet
            ? "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/40"
            : "border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950/40",
        )}
      >
        {allRequiredSet ? (
          <CheckCircle2Icon className="mt-0.5 size-5 shrink-0 text-green-600 dark:text-green-400" />
        ) : (
          <XCircleIcon className="mt-0.5 size-5 shrink-0 text-orange-500" />
        )}
        <div className="space-y-1">
          <p className="text-sm font-medium">
            {allRequiredSet
              ? "Hệ thống đã sẵn sàng hoạt động"
              : "Cần cấu hình các API key bắt buộc"}
          </p>
          <p className="text-muted-foreground text-xs">
            {allRequiredSet
              ? "DeepSeek và Telegram Bot đã được cấu hình. Bot có thể nhận tin nhắn."
              : "Điền DeepSeek API Key và Telegram Bot Token để khởi động hệ thống."}
          </p>
        </div>
      </div>

      {/* Required keys */}
      <SettingsSection
        title="API Keys Bắt buộc"
        description="Cần thiết để hệ thống hoạt động. Lấy tại platform.deepseek.com và @BotFather trên Telegram."
      >
        <div className="space-y-5">
          <KeyField
            label="DeepSeek API Key"
            description="Dùng cho cả Survey Agent và Architect Agent. Lấy tại: platform.deepseek.com/api_keys"
            placeholder="sk-..."
            isSet={config?.deepseek_api_key_set ?? false}
            hint={config?.deepseek_api_key_hint ?? ""}
            value={deepseekKey}
            onChange={setDeepseekKey}
            icon={<KeyRoundIcon className="size-3.5" />}
            required
          />
          <KeyField
            label="Telegram Bot Token"
            description="Token của Telegram Bot. Tạo bot và lấy token từ @BotFather trên Telegram."
            placeholder="123456789:AAHxxx..."
            isSet={config?.telegram_bot_token_set ?? false}
            hint={config?.telegram_bot_token_hint ?? ""}
            value={telegramToken}
            onChange={setTelegramToken}
            icon={<BotIcon className="size-3.5" />}
            required
          />
        </div>
      </SettingsSection>

      <Separator />

      {/* Optional keys */}
      <SettingsSection
        title="API Keys Tùy chọn"
        description="Mở rộng khả năng của Architect Agent — tìm kiếm web khi sinh proposal."
      >
        <KeyField
          label="Tavily API Key"
          description="Cho phép Architect Agent tìm kiếm thông tin công nghệ mới nhất. Lấy tại: tavily.com"
          placeholder="tvly-..."
          isSet={config?.tavily_api_key_set ?? false}
          hint={config?.tavily_api_key_hint ?? ""}
          value={tavilyKey}
          onChange={setTavilyKey}
          icon={<SearchIcon className="size-3.5" />}
        />
      </SettingsSection>

      <Separator />

      {/* Save button */}
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground text-xs">
          Keys được lưu vào file <code className="bg-muted rounded px-1 py-0.5">.env</code> trên
          server. Khởi động lại để áp dụng.
        </p>
        <Button onClick={handleSave} disabled={isPending} className="gap-2">
          {isPending ? (
            <Loader2Icon className="size-4 animate-spin" />
          ) : (
            <SaveIcon className="size-4" />
          )}
          Lưu cấu hình
        </Button>
      </div>
    </div>
  );
}
