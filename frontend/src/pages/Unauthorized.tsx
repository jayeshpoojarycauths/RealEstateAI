import React from 'react';
import { Link } from 'react-router-dom';
import {
    Card,
    CardHeader,
    CardBody,
    Typography,
    Button,
} from '@material-tailwind/react';
import { ShieldExclamationIcon } from '@heroicons/react/24/outline';
import { logger } from '../utils/logger';

export const Unauthorized: React.FC = () => {
    logger.warn('User accessed unauthorized page');

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <Card className="w-96">
                <CardHeader
                    variant="gradient"
                    color="red"
                    className="mb-4 grid h-28 place-items-center"
                >
                    <ShieldExclamationIcon className="h-12 w-12 text-white" />
                </CardHeader>
                <CardBody className="flex flex-col items-center gap-4">
                    <Typography variant="h4" color="blue-gray">
                        Access Denied
                    </Typography>
                    <Typography color="gray" className="text-center">
                        You don't have permission to access this page. Please contact your
                        administrator if you believe this is a mistake.
                    </Typography>
                    <Link to="/">
                        <Button color="blue" variant="gradient">
                            Return to Dashboard
                        </Button>
                    </Link>
                </CardBody>
            </Card>
        </div>
    );
}; 