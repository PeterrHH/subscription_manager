import React from 'react';
import {
  Box,
  Heading,
  Text,
  Badge,
  Button,
  HStack,
  VStack,
  Flex,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { ExternalLinkIcon, EditIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';

const SubscriptionCard = ({ 
  subscription, 
  onCancel, 
  onRestore, 
  isCancelled = false,
  showEditButton = true 
}) => {
  const { 
    id, 
    service_name, 
    price, 
    billing_cycle, 
    next_charge_date,
    cancellation_date,
    category, 
    management_link,
    send_reminder,
    reminder_time,
  } = subscription;
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const navigate = useNavigate();

  const formatDate = (dateString) => {
    console.log("DATE STRING {}",dateString);
    if (!dateString) return 'Not available';
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getCategoryColor = (category) => {
    switch(category) {
      case 'STREAMING': return 'purple';
      case 'MUSIC': return 'green';
      case 'SOFTWARE': return 'blue';
      default: return 'gray';
    }
  };

  const handleCancelClick = () => {
    onOpen();
  };

  const confirmCancel = () => {
    onCancel(id);
    onClose();
  };

  const getReminderText = () => {
    if (!send_reminder) return null;
    
    const reminderMap = {
      'SAME_DAY': 'on the due date',
      'ONE_DAY': '1 day before',
      'TWO_DAYS': '2 days before',
      'THREE_DAYS': '3 days before',
      'ONE_WEEK': '1 week before',
    };
    
    return `Reminder: ${reminderMap[reminder_time] || ''}`;
  };

  return (
    <>
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        p={5}
        bg="white"
        shadow="sm"
        transition="all 0.2s"
        _hover={{ shadow: 'md' }}
        position="relative"
      >
        <Tooltip label="Edit subscription">
          <IconButton
            icon={<EditIcon />}
            size="sm"
            aria-label="Edit subscription"
            position="absolute"
            top={2}
            right={2}
            onClick={() => navigate(`/edit/${id}`)}
          />
        </Tooltip>
        
        <Flex justify="space-between" align="flex-start" mb={3} mt={6}>
          <Heading size="md" fontWeight="semibold">{service_name}</Heading>
          <Badge colorScheme={getCategoryColor(category)}>
            {category.toLowerCase()}
          </Badge>
        </Flex>
        
        <Text fontSize="2xl" fontWeight="bold" color="purple.500" mb={2}>
          ${parseFloat(price).toFixed(2)}
          <Text as="span" fontSize="sm" color="gray.500" fontWeight="normal">
            /{billing_cycle.toLowerCase()}
          </Text>
        </Text>
        
        <Text color="gray.600" mb={2}>
          {isCancelled ? (
            `Cancelled on: ${formatDate(cancellation_date)}`
          ) : (
            `Next charge: ${formatDate(next_charge_date)}`
          )}
        </Text>
        
        {getReminderText() && (
          <Text color="blue.600" fontSize="sm" mb={4}>
            {getReminderText()}
          </Text>
        )}
        
        <HStack spacing={4} mt={4}>
          {management_link && (
            <Button
              size="sm"
              colorScheme="blue"
              variant="outline"
              rightIcon={<ExternalLinkIcon />}
              onClick={() => window.open(management_link, '_blank')}
            >
              Manage
            </Button>
          )}
          {!isCancelled && showEditButton && (
            <Button
              size="sm"
              colorScheme="blue"
              onClick={() => navigate(`/edit/${id}`)}
            >
              Edit
            </Button>
          )}
          
          {isCancelled ? (
            <Button
              size="sm"
              colorScheme="green"
              onClick={() => onRestore && onRestore(subscription)}
            >
              Restore
            </Button>
          ) : (
            <Button
              size="sm"
              colorScheme="red"
              onClick={() => onCancel && onCancel(id)}
            >
              Cancel
            </Button>
          )}
        </HStack>
      </Box>

      {/* Confirmation Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Cancel Subscription</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            Are you sure you want to cancel your {service_name} subscription? This will remove it from your active subscriptions.
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              No, Keep It
            </Button>
            <Button colorScheme="red" onClick={confirmCancel}>
              Yes, Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default SubscriptionCard; 