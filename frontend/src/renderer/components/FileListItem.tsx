import React from 'react';
import {
  ListItem,
  ListItemAvatar,
  Avatar,
  ListItemText,
  IconButton,
  Box,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageIcon from '@mui/icons-material/Image';
import { UploadedFile } from '../types';

interface FileListItemProps {
  file: UploadedFile;
  onRemove: () => void;
}

/**
 * FileListItem - Displays a single uploaded file with thumbnail and metadata
 * Features:
 * - Image thumbnail or placeholder icon
 * - File name and size
 * - Remove button
 */
const FileListItem: React.FC<FileListItemProps> = ({ file, onRemove }) => {
  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <ListItem
      sx={{
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        mb: 1,
        '&:hover': {
          bgcolor: 'action.hover',
        },
      }}
      secondaryAction={
        <IconButton
          edge="end"
          aria-label="delete"
          onClick={onRemove}
          size="small"
          color="error"
        >
          <DeleteIcon />
        </IconButton>
      }
    >
      <ListItemAvatar>
        {file.preview ? (
          <Avatar
            src={file.preview}
            variant="rounded"
            sx={{ width: 56, height: 56 }}
            alt={file.name}
          />
        ) : (
          <Avatar variant="rounded" sx={{ width: 56, height: 56 }}>
            <ImageIcon />
          </Avatar>
        )}
      </ListItemAvatar>
      <ListItemText
        primary={
          <Typography
            variant="body2"
            noWrap
            sx={{ maxWidth: '200px', fontWeight: 500 }}
          >
            {file.name}
          </Typography>
        }
        secondary={
          <Box component="span" sx={{ display: 'flex', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {formatFileSize(file.size)}
            </Typography>
          </Box>
        }
      />
    </ListItem>
  );
};

export default FileListItem;
