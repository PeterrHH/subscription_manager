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
} from '@chakra-ui/react';
import { ExternalLinkIcon } from '@chakra-ui/icons';

const SubscriptionCard = ({ subscription, onCancel }) => {
  const { 
    id, 
    service_name, 
    price, 
    billing_cycle, 
    next_charge_date, 
    category, 
    management_link 
  } = subscription;
  
  const { isOpen, onOpen, onClose } = useDisclosure();

  const formatDate = (dateString) => {
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
      >
        <Flex justify="space-between" align="flex-start" mb={3}>
          <Heading size="md" fontWeight="semibold">{service_name}</Heading>
          <Badge colorScheme={getCategoryColor(category)}>
            {category.toLowerCase()}
          </Badge>
        </Flex>
        
        <Text fontSize="2xl" fontWeight="bold" color="purple.500" mb={2}>
          ${price}
          <Text as="span" fontSize="sm" color="gray.500" fontWeight="normal">
            /{billing_cycle.toLowerCase()}
          </Text>
        </Text>
        
        <Text color="gray.600" mb={4}>
          Next charge: {formatDate(next_charge_date)}
        </Text>
        
        <HStack spacing={4} mt={2}>
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
          <Button
            size="sm"
            colorScheme="red"
            variant="outline"
            onClick={handleCancelClick}
          >
            Cancel
          </Button>
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