import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
    Card,
    CardHeader,
    CardBody,
    Typography,
    Button,
    Input,
    Checkbox,
} from '@material-tailwind/react';
import { useAuth } from '../hooks/useAuth';
import { logger } from '../utils/logger';

const loginSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(1, 'Password is required'),
    rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const Login: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();
    const [error, setError] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            rememberMe: false,
        },
    });

    const onSubmit = async (data: LoginFormData) => {
        try {
            setError(null);
            await login({
                email: data.email,
                password: data.password,
            });

            // Redirect to the page the user was trying to access, or dashboard
            const from = (location.state as any)?.from?.pathname || '/dashboard';
            navigate(from, { replace: true });

            logger.info('User logged in successfully', { email: data.email });
        } catch (err) {
            setError('Invalid email or password');
            logger.error('Login failed', err as Error, { email: data.email });
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <Card className="w-96">
                <CardHeader
                    variant="gradient"
                    color="blue"
                    className="mb-4 grid h-28 place-items-center"
                >
                    <Typography variant="h3" color="white">
                        Sign In
                    </Typography>
                </CardHeader>
                <CardBody className="flex flex-col gap-4">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div>
                            <Input
                                label="Email"
                                type="email"
                                {...register('email')}
                                error={!!errors.email}
                            />
                            {errors.email && (
                                <Typography
                                    variant="small"
                                    color="red"
                                    className="mt-1"
                                >
                                    {errors.email.message}
                                </Typography>
                            )}
                        </div>

                        <div>
                            <Input
                                label="Password"
                                type="password"
                                {...register('password')}
                                error={!!errors.password}
                            />
                            {errors.password && (
                                <Typography
                                    variant="small"
                                    color="red"
                                    className="mt-1"
                                >
                                    {errors.password.message}
                                </Typography>
                            )}
                        </div>

                        <div className="flex items-center">
                            <Checkbox
                                label="Remember me"
                                {...register('rememberMe')}
                            />
                        </div>

                        {error && (
                            <Typography
                                variant="small"
                                color="red"
                                className="text-center"
                            >
                                {error}
                            </Typography>
                        )}

                        <Button
                            type="submit"
                            color="blue"
                            variant="gradient"
                            fullWidth
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Signing in...' : 'Sign In'}
                        </Button>
                    </form>
                </CardBody>
            </Card>
        </div>
    );
}; 