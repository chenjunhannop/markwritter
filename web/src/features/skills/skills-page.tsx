import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertCircle, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { Skill, SkillInput } from "@/types/skills";
import { executeSkill, getSkills } from "./skills-api";

function SkillParamField({
  input,
  value,
  onChange,
}: {
  input: SkillInput;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  if (input.enum && input.enum.length > 0) {
    const selectId = `skill-param-${input.name}`;
    return (
      <div className="space-y-1">
        <label htmlFor={selectId} className="text-sm font-medium">
          {input.name}
          {input.required && <span className="text-destructive"> *</span>}
        </label>
        <Select
          value={(value as string) ?? (input.default as string) ?? ""}
          onValueChange={(v) => onChange(v)}
        >
          <SelectTrigger id={selectId}>
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {input.enum.map((opt) => (
              <SelectItem key={opt} value={opt}>
                {opt}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {input.description && (
          <p className="text-xs text-muted-foreground">{input.description}</p>
        )}
      </div>
    );
  }

  switch (input.type) {
    case "boolean":
      return (
        <div className="flex items-center gap-2">
          <Checkbox
            id={`skill-param-${input.name}`}
            checked={(value as boolean) ?? (input.default as boolean) ?? false}
            onCheckedChange={(v) => onChange(v === true)}
          />
          <label
            htmlFor={`skill-param-${input.name}`}
            className="text-sm font-medium"
          >
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
        </div>
      );
    case "number": {
      const numId = `skill-param-${input.name}`;
      return (
        <div className="space-y-1">
          <label htmlFor={numId} className="text-sm font-medium">
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
          <Input
            id={numId}
            type="number"
            value={(value as string) ?? (input.default as string) ?? ""}
            onChange={(e) => onChange(Number(e.target.value))}
          />
          {input.description && (
            <p className="text-xs text-muted-foreground">{input.description}</p>
          )}
        </div>
      );
    }
    default: {
      const textId = `skill-param-${input.name}`;
      return (
        <div className="space-y-1">
          <label htmlFor={textId} className="text-sm font-medium">
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
          <Input
            id={textId}
            value={(value as string) ?? (input.default as string) ?? ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={input.description}
          />
          {input.description && (
            <p className="text-xs text-muted-foreground">{input.description}</p>
          )}
        </div>
      );
    }
  }
}

function SkillRunDialog({
  skill,
  open,
  onOpenChange,
}: {
  skill: Skill;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [output, setOutput] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runMutation = useMutation({
    mutationFn: () => executeSkill(skill.name, params),
    onSuccess: (data) => {
      if (data.success) {
        setOutput(data.output);
        setError(null);
        toast.success("Skill executed successfully");
      } else {
        setError(data.error);
        setOutput(null);
        toast.error("Skill execution failed");
      }
    },
    onError: (err) => {
      setError(err.message);
      setOutput(null);
      toast.error("Skill execution failed");
    },
  });

  const handleParamChange = (name: string, value: unknown) => {
    setParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setParams({});
      setOutput(null);
      setError(null);
      runMutation.reset();
    }
    onOpenChange(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Run: {skill.name}</DialogTitle>
          <DialogDescription>{skill.description}</DialogDescription>
        </DialogHeader>

        {skill.inputs.length > 0 && (
          <div className="space-y-3">
            {skill.inputs.map((input) => (
              <SkillParamField
                key={input.name}
                input={input}
                value={params[input.name]}
                onChange={(v) => handleParamChange(input.name, v)}
              />
            ))}
          </div>
        )}

        {output && (
          <div className="rounded-md bg-muted p-3">
            <p className="text-sm font-medium mb-1">Output</p>
            <pre className="text-xs whitespace-pre-wrap">{output}</pre>
          </div>
        )}

        {error && (
          <div className="rounded-md bg-destructive/10 p-3">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Close
          </Button>
          <Button
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending}
          >
            {runMutation.isPending && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            Execute
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function SkillsPage() {
  const [runSkill, setRunSkill] = useState<Skill | null>(null);

  const {
    data: skills,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["skills"],
    queryFn: getSkills,
  });

  return (
    <div className="flex h-full flex-col gap-4 p-4 md:p-6">
      <h1 className="text-2xl font-bold">Skills</h1>

      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
            <div className="rounded-xl border p-4 space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-9 w-20" />
            </div>
          </div>
        )}

        {isError && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-sm text-muted-foreground">
              Failed to load skills.
            </p>
            <Button variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        )}

        {skills && skills.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
            <p className="text-muted-foreground">No skills available</p>
          </div>
        )}

        {skills && skills.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {skills.map((skill) => (
              <Card key={skill.name}>
                <CardHeader>
                  <CardTitle className="text-base">{skill.name}</CardTitle>
                  <CardDescription>{skill.description}</CardDescription>
                </CardHeader>
                <CardFooter>
                  <Button size="sm" onClick={() => setRunSkill(skill)}>
                    <Play className="h-3.5 w-3.5" />
                    Run
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>

      {runSkill && (
        <SkillRunDialog
          skill={runSkill}
          open={!!runSkill}
          onOpenChange={(open) => {
            if (!open) setRunSkill(null);
          }}
        />
      )}
    </div>
  );
}
