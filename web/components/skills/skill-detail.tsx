/**
 * SkillDetail Component
 *
 * Displays detailed skill information with a dynamic form for execution.
 * Uses React Hook Form + Zod for validation.
 */

import { useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, AlertCircle } from 'lucide-react';

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useSkillStore } from '@/lib/store';
import { useSkillExecution } from '@/hooks/use-skill-execution';
import { SkillExecutor } from './skill-executor';
import type { SkillInput } from '@/lib/types';

/**
 * Generate Zod schema from skill inputs
 */
function generateSchema(inputs: SkillInput[]) {
  const schemaFields: Record<string, z.ZodTypeAny> = {};

  for (const input of inputs) {
    let fieldSchema: z.ZodTypeAny;

    switch (input.type) {
      case 'string':
        fieldSchema = z.string();
        break;
      case 'number':
        fieldSchema = z.number();
        break;
      case 'boolean':
        fieldSchema = z.boolean();
        break;
      case 'enum':
        fieldSchema = z.string();
        break;
      default:
        fieldSchema = z.string();
    }

    if (!input.required && input.default !== undefined) {
      // Optional with default
      fieldSchema = fieldSchema.optional().default(input.default as never);
    } else if (!input.required) {
      fieldSchema = fieldSchema.optional();
    }

    schemaFields[input.name] = fieldSchema;
  }

  return z.object(schemaFields);
}

/**
 * Get default values from skill inputs
 */
function getDefaultValues(inputs: SkillInput[]): Record<string, unknown> {
  const defaults: Record<string, unknown> = {};

  for (const input of inputs) {
    if (input.default !== undefined) {
      defaults[input.name] = input.default;
    } else if (input.type === 'boolean') {
      defaults[input.name] = false;
    } else if (input.type === 'number') {
      defaults[input.name] = 0;
    } else {
      defaults[input.name] = '';
    }
  }

  return defaults;
}

/**
 * SkillDetail displays skill info and execution form.
 */
export function SkillDetail() {
  const { selectedSkill } = useSkillStore();
  const { status, result, error, execute, reset, isExecuting } = useSkillExecution();

  // Generate form schema and default values
  const formSchema = useMemo(() => {
    if (!selectedSkill) return null;
    return generateSchema(selectedSkill.inputs);
  }, [selectedSkill]);

  const defaultValues = useMemo(() => {
    if (!selectedSkill) return {};
    return getDefaultValues(selectedSkill.inputs);
  }, [selectedSkill]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset: resetForm,
    setValue,
    watch,
  } = useForm({
    resolver: formSchema ? zodResolver(formSchema) : undefined,
    defaultValues,
  });

  const onSubmit = async (data: Record<string, unknown>) => {
    if (!selectedSkill) return;
    await execute(selectedSkill.name, data);
  };

  const handleReset = () => {
    reset();
    resetForm(defaultValues);
  };

  // No skill selected
  if (!selectedSkill) {
    return (
      <div className="flex items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">No skill selected.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Skill Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-2xl">{selectedSkill.name}</CardTitle>
              <CardDescription className="mt-2">
                {selectedSkill.description}
              </CardDescription>
            </div>
            <Badge variant="secondary">{selectedSkill.version}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">
            Output: {selectedSkill.output.type} - {selectedSkill.output.description}
          </div>
        </CardContent>
      </Card>

      {/* Execution Form */}
      <Card>
        <CardHeader>
          <CardTitle>Execute Skill</CardTitle>
        </CardHeader>
        <CardContent>
          {selectedSkill.inputs.length === 0 ? (
            <p className="text-muted-foreground">No inputs required for this skill.</p>
          ) : (
            <form id="skill-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {selectedSkill.inputs.map((input) => (
                <div key={input.name} className="space-y-2">
                  <Label htmlFor={input.name}>
                    {input.name}
                    {input.required && <span className="text-destructive ml-1">*</span>}
                  </Label>

                  {input.type === 'boolean' ? (
                    <div className="flex items-center gap-2">
                      <Switch
                        id={input.name}
                        checked={watch(input.name) ?? false}
                        onCheckedChange={(checked) => setValue(input.name, checked)}
                      />
                      <span className="text-sm text-muted-foreground">
                        {watch(input.name) ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  ) : input.type === 'enum' && input.enum ? (
                    <Select
                      onValueChange={(value) => setValue(input.name, value)}
                      defaultValue={input.default as string}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={`Select ${input.name}`} />
                      </SelectTrigger>
                      <SelectContent>
                        {input.enum.map((option) => (
                          <SelectItem key={option} value={option}>
                            {option}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      id={input.name}
                      type={input.type === 'number' ? 'number' : 'text'}
                      step={input.type === 'number' ? 'any' : undefined}
                      aria-describedby={`${input.name}-description`}
                      {...register(input.name, {
                        valueAsNumber: input.type === 'number',
                      })}
                    />
                  )}

                  <p
                    id={`${input.name}-description`}
                    className="text-xs text-muted-foreground"
                  >
                    {input.description}
                  </p>

                  {errors[input.name] && (
                    <p className="text-xs text-destructive flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors[input.name]?.message?.toString() ||
                        (input.required ? 'Required' : 'Invalid value')}
                    </p>
                  )}
                </div>
              ))}
            </form>
          )}
        </CardContent>
        <CardFooter className="gap-2">
          <Button
            type="submit"
            form="skill-form"
            disabled={isExecuting() || selectedSkill.inputs.length === 0}
          >
            {isExecuting() ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Executing...
              </>
            ) : (
              'Execute'
            )}
          </Button>

          {(status === 'success' || status === 'error') && (
            <Button variant="outline" onClick={handleReset}>
              Reset
            </Button>
          )}
        </CardFooter>
      </Card>

      {/* Execution Result */}
      {(result || error) && <SkillExecutor result={result} error={error} />}
    </div>
  );
}