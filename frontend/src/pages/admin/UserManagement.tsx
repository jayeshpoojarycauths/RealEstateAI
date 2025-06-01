import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Role, User } from '../../types/auth';
import { useUsers } from '../../hooks/useUsers';
import { logger } from '../../utils/logger';
import {
    SafeCard,
    SafeCardHeader,
    SafeCardBody,
    SafeTypography,
    SafeButton,
    SafeInput,
    SafeSelect,
    SafeOption,
} from '../../components/SafeMTW';

const createUserSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    firstName: z.string().min(1, 'First name is required'),
    lastName: z.string().min(1, 'Last name is required'),
    role: z.nativeEnum(Role),
});

type CreateUserFormData = z.infer<typeof createUserSchema>;

export const UserManagement: React.FC = () => {
    const { users, createUser, updateUser, deleteUser, isLoading, error } = useUsers();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
        control,
    } = useForm<CreateUserFormData>({
        resolver: zodResolver(createUserSchema),
    });

    const onSubmit = async (data: CreateUserFormData) => {
        try {
            await createUser(data);
            setIsCreateModalOpen(false);
            reset();
            logger.info('User created successfully', { email: data.email });
        } catch (error) {
            logger.error('Failed to create user', { error, email: data.email });
        }
    };

    const handleDeleteUser = async (userId: string) => {
        try {
            await deleteUser(userId);
            logger.info('User deleted successfully', { userId });
        } catch (error) {
            logger.error('Failed to delete user', { error, userId });
        }
    };

    return (
        <div className="p-4">
            <SafeCard>
                <SafeCardHeader
                    variant="gradient"
                    color="blue"
                    className="mb-4 grid h-28 place-items-center"
                >
                    <SafeTypography variant="h3" color="white">
                        User Management
                    </SafeTypography>
                </SafeCardHeader>
                <SafeCardBody className="overflow-x-auto px-0 pt-0 pb-2">
                    <div className="flex justify-end mb-4">
                        <SafeButton
                            color="blue"
                            onClick={() => setIsCreateModalOpen(true)}
                        >
                            Create User
                        </SafeButton>
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
                                        <SafeTypography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Name
                                        </SafeTypography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <SafeTypography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Email
                                        </SafeTypography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <SafeTypography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Role
                                        </SafeTypography>
                                    </th>
                                    <th className="border-b border-blue-gray-50 py-3 px-6 text-left">
                                        <SafeTypography
                                            variant="small"
                                            className="text-[11px] font-medium uppercase text-blue-gray-400"
                                        >
                                            Actions
                                        </SafeTypography>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {users?.map((user) => (
                                    <tr key={user.id}>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <SafeTypography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.firstName} {user.lastName}
                                            </SafeTypography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <SafeTypography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.email}
                                            </SafeTypography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <SafeTypography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {user.role}
                                            </SafeTypography>
                                        </td>
                                        <td className="py-3 px-6 border-b border-blue-gray-50">
                                            <div className="flex space-x-2">
                                                <SafeButton
                                                    size="sm"
                                                    variant="outlined"
                                                    color="blue"
                                                    onClick={() => updateUser(user.id, { role: user.role })}
                                                >
                                                    Edit
                                                </SafeButton>
                                                <SafeButton
                                                    size="sm"
                                                    variant="outlined"
                                                    color="red"
                                                    onClick={() => handleDeleteUser(user.id)}
                                                >
                                                    Delete
                                                </SafeButton>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </SafeCardBody>
            </SafeCard>

            {/* Create User Modal */}
            {isCreateModalOpen && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="modal-title"
                >
                    <SafeCard className="w-96">
                        <SafeCardHeader
                            variant="gradient"
                            color="blue"
                            className="mb-4 grid h-28 place-items-center"
                        >
                            <SafeTypography id="modal-title" variant="h3" color="white">
                                Create User
                            </SafeTypography>
                        </SafeCardHeader>
                        <SafeCardBody>
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                                <div>
                                    <SafeInput
                                        label="Email"
                                        type="email"
                                        {...register('email')}
                                        error={!!errors.email}
                                    />
                                    {errors.email && (
                                        <SafeTypography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.email.message}
                                        </SafeTypography>
                                    )}
                                </div>

                                <div>
                                    <SafeInput
                                        label="Password"
                                        type="password"
                                        {...register('password')}
                                        error={!!errors.password}
                                    />
                                    {errors.password && (
                                        <SafeTypography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.password.message}
                                        </SafeTypography>
                                    )}
                                </div>

                                <div>
                                    <SafeInput
                                        label="First Name"
                                        {...register('firstName')}
                                        error={!!errors.firstName}
                                    />
                                    {errors.firstName && (
                                        <SafeTypography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.firstName.message}
                                        </SafeTypography>
                                    )}
                                </div>

                                <div>
                                    <SafeInput
                                        label="Last Name"
                                        {...register('lastName')}
                                        error={!!errors.lastName}
                                    />
                                    {errors.lastName && (
                                        <SafeTypography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.lastName.message}
                                        </SafeTypography>
                                    )}
                                </div>

                                <div>
                                    <Controller
                                        name="role"
                                        control={control}
                                        render={({ field }) => (
                                            <SafeSelect
                                                label="Role"
                                                value={field.value}
                                                onChange={field.onChange}
                                                error={!!errors.role}
                                            >
                                                {Object.values(Role).map((role) => (
                                                    <SafeOption key={role} value={role}>
                                                        {role}
                                                    </SafeOption>
                                                ))}
                                            </SafeSelect>
                                        )}
                                    />
                                    {errors.role && (
                                        <SafeTypography
                                            variant="small"
                                            color="red"
                                            className="mt-1"
                                        >
                                            {errors.role.message}
                                        </SafeTypography>
                                    )}
                                </div>

                                <div className="flex justify-end space-x-2">
                                    <SafeButton
                                        variant="outlined"
                                        color="red"
                                        onClick={() => {
                                            setIsCreateModalOpen(false);
                                            reset();
                                        }}
                                    >
                                        Cancel
                                    </SafeButton>
                                    <SafeButton type="submit" color="blue">
                                        Create
                                    </SafeButton>
                                </div>
                            </form>
                        </SafeCardBody>
                    </SafeCard>
                </div>
            )}
        </div>
    );
}; 