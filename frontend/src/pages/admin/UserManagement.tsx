import React, { useState } from 'react';
import {
    Card,
    CardHeader,
    CardBody,
    Typography,
    Button,
    Input,
    Select,
    Option,
} from '@material-tailwind/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../../hooks/useAuth';
import { Role } from '../../types/auth';
import { useUsers } from '../../hooks/useUsers';
import { logger } from '../../utils/logger';

const createUserSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    firstName: z.string().min(1, 'First name is required'),
    lastName: z.string().min(1, 'Last name is required'),
    role: z.nativeEnum(Role),
});

type CreateUserFormData = z.infer<typeof createUserSchema>;

export const UserManagement: React.FC = () => {
    const { user } = useAuth();
    const { users, createUser, updateUser, deleteUser, isLoading, error } = useUsers();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
    } = useForm<CreateUserFormData>({
        resolver: zodResolver(createUserSchema),
    });

    const onSubmit = async (data: CreateUserFormData) => {
        try {
            await createUser(data);
            setIsCreateModalOpen(false);
            reset();
            logger.info('User created successfully', { email: data.email, role: data.role });
        } catch (error) {
            logger.error('Failed to create user', error as Error, { email: data.email });
        }
    };

    const handleDeleteUser = async (userId: string) => {
        try {
            await deleteUser(userId);
            logger.info('User deleted successfully', { userId });
        } catch (error) {
            logger.error('Failed to delete user', error as Error, { userId });
        }
    };

    const handleUpdateUser = async (userId: string, userData: Partial<CreateUserFormData>) => {
        try {
            await updateUser(userId, userData);
            setSelectedUser(null);
            logger.info('User updated successfully', { userId });
        } catch (error) {
            logger.error('Failed to update user', error as Error, { userId });
        }
    };

    return (
        <div className="p-4">
            <Card>
                <CardHeader
                    variant="gradient"
                    color="blue"
                    className="mb-4 grid h-28 place-items-center"
                >
                    <Typography variant="h3" color="white">
                        User Management
                    </Typography>
                </CardHeader>
                <CardBody className="overflow-x-auto px-0 pt-0 pb-2">
                    <div className="flex justify-end mb-4">
                        <Button
                            color="blue"
                            onClick={() => setIsCreateModalOpen(true)}
                        >
                            Create User
                        </Button>
                    </div>

                    {isLoading ? (
                        <div>Loading...</div>
                    ) : error ? (
                        <div>Error: {error.message}</div>
                    ) : (
                        <table className="w-full min-w-[640px] table-auto">
                            <thead>
                                <tr>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <Typography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Name
                                        </Typography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <Typography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Email
                                        </Typography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <Typography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Role
                                        </Typography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <Typography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Status
                                        </Typography>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {users?.map((user) => (
                                    <tr key={user.id}>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <Typography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.firstName} {user.lastName}
                                            </Typography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <Typography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.email}
                                            </Typography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <Typography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.role}
                                            </Typography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <Typography
                                                variant="small"
                                                color={user.isActive ? 'green' : 'red'}
                                                className="font-normal"
                                            >
                                                {user.isActive ? 'Active' : 'Inactive'}
                                            </Typography>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </CardBody>
            </Card>

            {/* Create User Modal */}
            {isCreateModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <Card className="w-96">
                        <CardHeader
                            variant="gradient"
                            color="blue"
                            className="mb-4 grid h-28 place-items-center"
                        >
                            <Typography variant="h3" color="white">
                                Create User
                            </Typography>
                        </CardHeader>
                        <CardBody>
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

                                <div>
                                    <Input
                                        label="First Name"
                                        {...register('firstName')}
                                        error={!!errors.firstName}
                                    />
                                    {errors.firstName && (
                                        <Typography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.firstName.message}
                                        </Typography>
                                    )}
                                </div>

                                <div>
                                    <Input
                                        label="Last Name"
                                        {...register('lastName')}
                                        error={!!errors.lastName}
                                    />
                                    {errors.lastName && (
                                        <Typography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.lastName.message}
                                        </Typography>
                                    )}
                                </div>

                                <div>
                                    <Select
                                        label="Role"
                                        {...register('role')}
                                        error={!!errors.role}
                                    >
                                        {Object.values(Role).map((role) => (
                                            <Option key={role} value={role}>
                                                {role}
                                            </Option>
                                        ))}
                                    </Select>
                                    {errors.role && (
                                        <Typography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.role.message}
                                        </Typography>
                                    )}
                                </div>

                                <div className="flex justify-end space-x-2">
                                    <Button
                                        variant="outlined"
                                        color="red"
                                        onClick={() => setIsCreateModalOpen(false)}
                                    >
                                        Cancel
                                    </Button>
                                    <Button type="submit" color="blue">
                                        Create
                                    </Button>
                                </div>
                            </form>
                        </CardBody>
                    </Card>
                </div>
            )}
        </div>
    );
}; 