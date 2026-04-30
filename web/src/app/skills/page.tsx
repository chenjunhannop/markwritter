import { BaseLayout } from "@/components/layouts/base-layout";
import { SkillsPage as SkillsPageContent } from "@/features/skills/skills-page";

export default function SkillsPage() {
  return (
    <BaseLayout title="Skills">
      <SkillsPageContent />
    </BaseLayout>
  );
}
