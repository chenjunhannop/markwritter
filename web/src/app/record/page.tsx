import { BaseLayout } from "@/components/layouts/base-layout";
import { RecordPage as RecordPageContent } from "@/features/record/record-page";

export default function RecordPage() {
  return (
    <BaseLayout>
      <div className="h-[calc(100vh-var(--header-height)-4rem)]">
        <RecordPageContent />
      </div>
    </BaseLayout>
  );
}
