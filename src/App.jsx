import React, { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { Button, Layout, Menu } from 'antd';

import LoginPage from './Components/LoginPage/LoginPage';
import RegisterPage from './Components/RegisterPage/RegisterPage';
import LandingPage from './Components/LandingPage/LandingPage';
import SavedJobs from './Components/SavedJobs/SavedJobs';
import RecommendedJobs from './Components/RecommendedJobs/RecommendedJobs';
import './App.scss';

const { Header, Content } = Layout;

const signedInPages = {
	'/home': 'My Applications',
	'/interested': 'Saved Jobs',
	'/recommended': 'Recommended',
};

export default function App() {
	const { state, pathname } = useLocation();
	const [selectedMenu, setSelectedMenu] = useState(pathname);
	const navigate = useNavigate();

	useEffect(() => {
		if ((!state || !state.email) && !['/login', '/register'].includes(pathname)) {
			navigate('/login');
		} else if (state && state.email && ['/login', '/register'].includes(pathname)) {
			navigate('/home', { state });
		}
		setSelectedMenu(pathname);
	}, [state, pathname]);

	const browsePage = ({ key }) => {
		navigate(key, { state });
		setSelectedMenu(key);
	};

	const logout = () => {
		axios.post('/api/logout');
		navigate('/login', { state: { email: undefined } });
	};

	if (state && state.email) {
		return (
			<Layout className="App">
				<Header>
					<div className="logo" />
					<Menu
						theme="dark"
						mode="horizontal"
						items={Object.keys(signedInPages).map((i) => ({
							key: i,
							label: signedInPages[i],
						}))}
						selectedKeys={[selectedMenu]}
						onSelect={browsePage}
					/>
					<div className="flex" />
					<Button type="primary" danger onClick={logout}>
						Logout
					</Button>
				</Header>
				<Content className="Content">
					<Routes>
						<Route path="/home" element={<LandingPage />} />
						<Route path="/interested" element={<SavedJobs />} />
						<Route path="/recommended" element={<RecommendedJobs />} />
						<Route path="*" element={<Navigate to="/home" replace />} />
					</Routes>
				</Content>
			</Layout>
		);
	}

	return (
		<Routes>
			<Route path="/login" element={<LoginPage />} />
			<Route path="/register" element={<RegisterPage />} />
			<Route path="*" element={<Navigate to="/login" replace />} />
		</Routes>
	);
}
