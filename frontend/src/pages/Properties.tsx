import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Card,
    CardHeader,
    CardBody,
    Typography,
    Button,
    Input,
    Select,
    Option,
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
} from '@material-tailwind/react';
import { z } from 'zod';
import { propertyService } from '../services/propertyService';
import { Property, CreatePropertyDto, PropertyFilters } from '../types/property';
import { LoadingTable, LoadingOverlay } from '../components/common/LoadingStates';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { useToast } from '../components/common/Toast';
import { logger } from '../utils/logger';

const propertySchema = z.object({
    title: z.string().min(1, 'Title is required'),
    description: z.string().min(1, 'Description is required'),
    address: z.string().min(1, 'Address is required'),
    price: z.number().positive('Price must be positive'),
    status: z.enum(['available', 'sold', 'pending']),
    type: z.enum(['residential', 'commercial', 'land']),
    bedrooms: z.number().optional(),
    bathrooms: z.number().optional(),
    area: z.number().positive('Area must be positive'),
    features: z.array(z.string()),
});

export const Properties: React.FC = () => {
    const queryClient = useQueryClient();
    const { showToast } = useToast();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<Property['status'] | ''>('');
    const [typeFilter, setTypeFilter] = useState<Property['type'] | ''>('');
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newProperty, setNewProperty] = useState<Partial<CreatePropertyDto>>({});

    const filters: PropertyFilters = {
        search: searchTerm,
        status: statusFilter || undefined,
        type: typeFilter || undefined,
    };

    const { data: properties, isLoading, error } = useQuery({
        queryKey: ['properties', filters],
        queryFn: () => propertyService.getAll(filters),
    });

    const createMutation = useMutation({
        mutationFn: (property: CreatePropertyDto) => propertyService.create(property),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['properties'] });
            setIsAddModalOpen(false);
            setNewProperty({});
            showToast('success', 'Property created successfully');
        },
        onError: (error) => {
            logger.error('Failed to create property:', error);
            showToast('error', 'Failed to create property');
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (id: string) => propertyService.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['properties'] });
            showToast('success', 'Property deleted successfully');
        },
        onError: (error) => {
            logger.error('Failed to delete property:', error);
            showToast('error', 'Failed to delete property');
        },
    });

    const handleCreateProperty = async () => {
        try {
            const validatedData = propertySchema.parse(newProperty);
            await createMutation.mutateAsync(validatedData);
        } catch (error) {
            if (error instanceof z.ZodError) {
                showToast('error', error.errors[0].message);
            } else {
                showToast('error', 'Invalid property data');
            }
        }
    };

    if (isLoading) {
        return <LoadingTable columns={6} rows={5} />;
    }

    if (error) {
        return (
            <ErrorBoundary>
                <Card className="w-full">
                    <CardBody>
                        <Typography color="red">Error loading properties</Typography>
                    </CardBody>
                </Card>
            </ErrorBoundary>
        );
    }

    return (
        <div className="p-4">
            <div className="flex justify-between items-center mb-4">
                <Typography variant="h4">Properties</Typography>
                <Button
                    color="blue"
                    onClick={() => setIsAddModalOpen(true)}
                >
                    Add Property
                </Button>
            </div>

            <div className="flex gap-4 mb-4">
                <Input
                    label="Search"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="max-w-xs"
                />
                <Select
                    label="Status"
                    value={statusFilter}
                    onChange={(value) => setStatusFilter(value as Property['status'])}
                    className="max-w-xs"
                >
                    <Option value="">All</Option>
                    <Option value="available">Available</Option>
                    <Option value="sold">Sold</Option>
                    <Option value="pending">Pending</Option>
                </Select>
                <Select
                    label="Type"
                    value={typeFilter}
                    onChange={(value) => setTypeFilter(value as Property['type'])}
                    className="max-w-xs"
                >
                    <Option value="">All</Option>
                    <Option value="residential">Residential</Option>
                    <Option value="commercial">Commercial</Option>
                    <Option value="land">Land</Option>
                </Select>
            </div>

            <Card>
                <CardBody>
                    <table className="w-full">
                        <thead>
                            <tr>
                                <th className="text-left p-4">Title</th>
                                <th className="text-left p-4">Address</th>
                                <th className="text-left p-4">Price</th>
                                <th className="text-left p-4">Status</th>
                                <th className="text-left p-4">Type</th>
                                <th className="text-left p-4">Area</th>
                                <th className="text-left p-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {properties?.map((property) => (
                                <tr key={property.id}>
                                    <td className="p-4">{property.title}</td>
                                    <td className="p-4">{property.address}</td>
                                    <td className="p-4">${property.price.toLocaleString()}</td>
                                    <td className="p-4">{property.status}</td>
                                    <td className="p-4">{property.type}</td>
                                    <td className="p-4">{property.area} sq ft</td>
                                    <td className="p-4">
                                        <Button
                                            color="red"
                                            size="sm"
                                            onClick={() => deleteMutation.mutate(property.id)}
                                        >
                                            Delete
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </CardBody>
            </Card>

            <Dialog open={isAddModalOpen} handler={() => setIsAddModalOpen(false)}>
                <DialogHeader>Add New Property</DialogHeader>
                <DialogBody>
                    <div className="space-y-4">
                        <Input
                            label="Title"
                            value={newProperty.title || ''}
                            onChange={(e) => setNewProperty({ ...newProperty, title: e.target.value })}
                        />
                        <Input
                            label="Description"
                            value={newProperty.description || ''}
                            onChange={(e) => setNewProperty({ ...newProperty, description: e.target.value })}
                        />
                        <Input
                            label="Address"
                            value={newProperty.address || ''}
                            onChange={(e) => setNewProperty({ ...newProperty, address: e.target.value })}
                        />
                        <Input
                            type="number"
                            label="Price"
                            value={newProperty.price || ''}
                            onChange={(e) => setNewProperty({ ...newProperty, price: Number(e.target.value) })}
                        />
                        <Select
                            label="Status"
                            value={newProperty.status || ''}
                            onChange={(value) => setNewProperty({ ...newProperty, status: value as Property['status'] })}
                        >
                            <Option value="available">Available</Option>
                            <Option value="sold">Sold</Option>
                            <Option value="pending">Pending</Option>
                        </Select>
                        <Select
                            label="Type"
                            value={newProperty.type || ''}
                            onChange={(value) => setNewProperty({ ...newProperty, type: value as Property['type'] })}
                        >
                            <Option value="residential">Residential</Option>
                            <Option value="commercial">Commercial</Option>
                            <Option value="land">Land</Option>
                        </Select>
                        <Input
                            type="number"
                            label="Area (sq ft)"
                            value={newProperty.area || ''}
                            onChange={(e) => setNewProperty({ ...newProperty, area: Number(e.target.value) })}
                        />
                    </div>
                </DialogBody>
                <DialogFooter>
                    <Button
                        variant="text"
                        color="red"
                        onClick={() => setIsAddModalOpen(false)}
                        className="mr-1"
                    >
                        Cancel
                    </Button>
                    <Button
                        color="blue"
                        onClick={handleCreateProperty}
                        disabled={createMutation.isPending}
                    >
                        {createMutation.isPending ? 'Creating...' : 'Create'}
                    </Button>
                </DialogFooter>
            </Dialog>

            <LoadingOverlay show={createMutation.isPending} message="Creating property..." />
        </div>
    );
}; 