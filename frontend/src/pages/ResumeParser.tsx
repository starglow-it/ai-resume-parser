// ** React Imports
import { useState, ChangeEvent, MouseEvent } from 'react';
import axios, { CancelTokenSource } from 'axios';

// ** MUI Imports
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Alert from '@mui/material/Alert';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import { styled } from '@mui/material/styles';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import AlertTitle from '@mui/material/AlertTitle';
import IconButton from '@mui/material/IconButton';
import CardContent from '@mui/material/CardContent';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import LinearProgress from '@mui/material/LinearProgress';
import { Container, Input } from '@mui/material';

import Close from 'mdi-material-ui/Close';

// Styled Components
const ImgStyled = styled('img')(({ theme }) => ({
    width: 80,
    height: 80,
    marginRight: theme.spacing(6.25),
    borderRadius: theme.shape.borderRadius,
}));

const ResetButtonStyled = styled(Button)(({ theme }) => ({
    marginLeft: theme.spacing(4.5),
    [theme.breakpoints.down('sm')]: {
        width: '100%',
        marginLeft: 0,
        textAlign: 'center',
        marginTop: theme.spacing(4),
    },
}));

// Component
const ResumeParser = () => {
    // ** State
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [format, setFormat] = useState<'json' | 'spreadsheet'>('json');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [messages, setMessages] = useState<String>('');
    const [showAlert, setShowAlert] = useState<boolean>(false);
    const [requestCancelToken, setRequestCancelToken] = useState<CancelTokenSource | undefined>(undefined);

    const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];

        if (file) {
            if (/\.(pdf|docx?)$/i.test(file.name) && file.size <= 5 * 1024 * 1024) {
                setShowAlert(false);
                setSelectedFile(file);
            } else {
                setError('This file was not accepted. Only PDF, DOCX, or DOC files under 5MB are allowed.');
                setShowAlert(true);
                setSelectedFile(null);
                setMessages('');
            }
        } else {
            setError('No file selected.');
            setShowAlert(true);
            setSelectedFile(null);
            setMessages('');
        }
    };

    const handleReset = () => {
        setSelectedFile(null);
        setError('');
        setMessages('');
    };

    const handleChange = (event: SelectChangeEvent<'json' | 'spreadsheet'>) => {
        setFormat(event.target.value as 'json' | 'spreadsheet');
    };

    const onSubmit = async (e: MouseEvent<HTMLButtonElement>) => {
        e.preventDefault();

        if (!selectedFile) {
            setError('Resume is not selected. Please upload a resume.');
            setShowAlert(true);
            setMessages('');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('format', format);
        formData.append('output_folder', '');

        setIsLoading(true);
        try {
            const CancelTokenSource = axios.CancelToken.source();
            setRequestCancelToken(CancelTokenSource);

            const response = await axios.post('http://localhost:5000/parse-resume', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                cancelToken: CancelTokenSource.token,
            });

            setMessages(response.data?.message);
            setError('');
        } catch (error) {
            if (axios.isAxiosError(error) && error.response) {
                setError(error.response.data.error || 'An unexpected error occurred.');
            }
            setMessages('');
        } finally {
            setIsLoading(false);
            setShowAlert(true);
        }
    };

    const handleCancelRequest = () => {
        if (requestCancelToken) {
            requestCancelToken.cancel('User cancelled the request');
        }
    };

    return (
        <Container maxWidth="md">
            <CardContent>
                <form>
                    <Grid container spacing={7}>
                        <Grid item xs={12} sx={{ marginTop: 4.8, marginBottom: 3 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <ImgStyled src='/images/ocr.svg' alt='Resume Pic' />
                                <Box>
                                    <Input
                                        type="file"
                                        inputProps={{ accept: '.pdf, .docx, .doc' }}
                                        onChange={handleFileInputChange}
                                    />
                                    <ResetButtonStyled color='error' variant='outlined' onClick={handleReset}>
                                        Reset
                                    </ResetButtonStyled>
                                    {selectedFile && (
                                        <Typography variant="body1" sx={{ marginTop: 2 }}>
                                            Selected File: {selectedFile.name}
                                        </Typography>
                                    )}

                                </Box>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth>
                                <InputLabel>Output Format</InputLabel>
                                <Select label='Output Format' onChange={handleChange} value={format}>
                                    <MenuItem value='json'>JSON</MenuItem>
                                    <MenuItem value='spreadsheet'>Spreadsheet</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>

                        <Grid item xs={12}>
                            <Button variant='contained' sx={{ marginRight: 3.5 }} onClick={onSubmit}>
                                Parse Resumes
                            </Button>
                            <Button type='reset' variant='outlined' color='secondary' onClick={handleCancelRequest}>
                                Cancel
                            </Button>
                        </Grid>
                    </Grid>
                </form>
            </CardContent>
            {isLoading &&
                (
                    <Box sx={{ padding: 2 }}>
                        <LinearProgress />
                    </Box>
                )
            }
            <Box sx={{ padding: 2 }}>
                <Grid item xs={12} sx={{ mb: 3 }}>
                    {(showAlert && error) && (
                        <Alert
                            severity='warning'
                            sx={{ '& a': { fontWeight: 400 } }}
                            action={
                                <IconButton size='small' color='inherit' aria-label='close' onClick={() => setShowAlert(false)}>
                                    <Close fontSize='inherit' />
                                </IconButton>
                            }
                        >
                            <AlertTitle>{error}</AlertTitle>
                        </Alert>
                    )}
                    {(showAlert && Boolean(messages)) && (
                        <Alert
                            severity='success'
                            sx={{ '& a': { fontWeight: 400 } }}
                            action={
                                <IconButton size='small' color='inherit' aria-label='close' onClick={() => setShowAlert(false)}>
                                    <Close fontSize='inherit' />
                                </IconButton>
                            }
                        >
                            <AlertTitle>{messages}</AlertTitle>
                        </Alert>
                    )}
                </Grid>
            </Box>
        </Container>
    );
};

export default ResumeParser;