import { BaseLayout } from "@/components/layouts/base-layout";
import { QueryPage as QueryPageContent } from "@/features/query/query-page";

export default function QueryPage() {
  return (
    <BaseLayout title="Query">
      <QueryPageContent />
    </BaseLayout>
  );
}
