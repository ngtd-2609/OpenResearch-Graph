import { z } from "zod";

const passwordSchema = z
  .string()
  .min(8, "Mật khẩu cần ít nhất 8 ký tự")
  .max(128, "Mật khẩu quá dài")
  .regex(/[A-Za-z]/, "Mật khẩu phải có chữ cái")
  .regex(/\d/, "Mật khẩu phải có chữ số");

export const registerSchema = z
  .object({
    email: z.string().trim().email("Email không hợp lệ"),
    username: z
      .string()
      .trim()
      .min(3, "Tên đăng nhập cần ít nhất 3 ký tự")
      .max(80)
      .regex(/^[A-Za-z0-9_.-]+$/, "Tên đăng nhập chứa ký tự không hợp lệ"),
    password: passwordSchema,
    passwordConfirmation: z.string(),
    full_name: z.string().trim().max(160).optional(),
  })
  .refine((values) => values.password === values.passwordConfirmation, {
    message: "Mật khẩu nhập lại không khớp",
    path: ["passwordConfirmation"],
  });

export const loginSchema = z.object({
  email: z.string().trim().email("Email không hợp lệ"),
  password: z.string().min(1, "Vui lòng nhập mật khẩu"),
});

export const searchSchema = z
  .object({
    query: z.string().trim().min(2).max(300),
    fromYear: z.coerce.number().int().min(1900).optional(),
    toYear: z.coerce.number().int().min(1900).optional(),
  })
  .refine(
    (values) => !values.fromYear || !values.toYear || values.fromYear <= values.toYear,
    { message: "Năm bắt đầu phải nhỏ hơn hoặc bằng năm kết thúc", path: ["toYear"] },
  );

export type RegisterValues = z.infer<typeof registerSchema>;
export type LoginValues = z.infer<typeof loginSchema>;
export type SearchValues = z.infer<typeof searchSchema>;
