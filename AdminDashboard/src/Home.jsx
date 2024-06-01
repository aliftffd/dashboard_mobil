import React, { useEffect, useState } from 'react';
import { MdOutlineSpeed, MdTrain, MdLocationOn } from 'react-icons/md';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import GaugeComponent from 'react-gauge-component';
import io from 'socket.io-client';

const MAX_DATA_COUNT = 20;
const MAX_SPEED = 100;
const gaugeLimits = [
  { limit: 20, color: '#5BE12C', showTick: true },
  { limit: 40, color: '#F5CD19', showTick: true },
  { limit: 60, color: '#F58B19', showTick: true },
  { limit: MAX_SPEED, color: '#EA4228', showTick: true },
];

function Home() {
  const [sensorData, setSensorData] = useState([]);
  const [socketConnected, setSocketConnected] = useState(false);
  const [gaugeValue, setGaugeValue] = useState(0);
  const [distanceData, setDistanceData] = useState([]);
  const [totalDistance, setTotalDistance] = useState(0);
  const [prevTimestamp, setPrevTimestamp] = useState(null);
  const [rfidData, setRfidData] = useState([]);

  const kmhToMs = (value) => {
    if (value === undefined) {
      return { value: 'N/A', unit: 'km/h' };
    }
    return { value: value, unit: 'km/h' };
  };

  useEffect(() => {
    const URL1 = "http://localhost:5001";
    const URL2 = "http://localhost:5000"
    const socket1 = io(URL1, {
      pingTimeout: 30000,
      pingInterval: 5000,
      upgradeTimeout: 30000,
      cors: {
        origin: "http://localhost:5173",
      }
    });
    const socket2 = io(URL2,{
      pingTimeout: 30000,
      pingInterval: 5000,
      upgradeTimeout: 30000,
      cors: {
        origin: "http://localhost:5173",
      }
    });

    socket1.connect();
    socket2.connect(); 

    socket1.on("connect_error", (err) => {
      console.log(`connect_error due to ${err.message}`);
    });
    socket2.on("conncect_error",(err) =>{
      console.log(`connect_error due to ${err.message}`);
    })

    socket1.on('connect', () => {
      setSocketConnected(true);
    });

    socket1.on('disconnect', () => {
      setSocketConnected(false);
    });

    socket2.on('connect', () => {
      setSocketConnected(true);
    });

    socket2.on('disconnect', () => {
      setSocketConnected(false);
    });


    socket1.on('sensorData', (data) => {
      const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
      const { value, timestamp } = parsedData;
      const newTimestamp = new Date(timestamp).getTime();
    
      setSensorData(prevData => {
        const newData = [...prevData, { date: newTimestamp, speed: value }].slice(-MAX_DATA_COUNT);
        setGaugeValue(value);
    
        if (prevTimestamp !== null) {
          const timeDiff = (newTimestamp - prevTimestamp) / 3600000; // time difference in hours
          const incrementalDistance = value * timeDiff; // distance in kilometers
    
          setTotalDistance(prevDistance => {
            const updatedDistance = prevDistance + incrementalDistance;
            return parseFloat(updatedDistance.toFixed(2)); // ensure two decimal places
          });
    
          const updatedDistanceData = newData.map((point, index) => ({
            ...point,
            distance: (index === 0 ? 0 : (totalDistance + incrementalDistance)).toFixed(2),
          }));
    
          setDistanceData(updatedDistanceData);
        }
    
        setPrevTimestamp(newTimestamp);
        return newData;
      });
    });
    
    socket2.on('rfid_data', (data) => {
      console.log('Received rfid_data event:', data); // Log the received data
  
      try {
          const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
          console.log('Parsed data:', parsedData); // Log the parsed data
  
          setRfidData(prevData => {
              const updatedData = [...prevData, parsedData].slice(-MAX_DATA_COUNT);
              console.log('Updated rfidData state:', updatedData); // Log the updated state
              return updatedData;
          });
      } catch (error) {
          console.error('Error parsing data:', error); // Log any parsing errors
      }
  });
    return () => {
      socket1.disconnect();
      socket2.disconnect();
    };
  }, [prevTimestamp, totalDistance]);

  const lastSensorData = sensorData.length > 0 ? sensorData[sensorData.length - 1].speed : 0;
  const { value: convertedValue, unit: speedUnit } = kmhToMs(lastSensorData);
  
  return (
    <main className='main-container'>
      <div className='main-title'>
        <h1>DASHBOARD</h1>
      </div>
      <div className='main-cards'>
        <div className='card'>
          <div className='card-inner'>
            <h3>Speed Rated</h3>
            <MdOutlineSpeed className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2 id='speedValue'>{convertedValue}</h2>
            <span className="unit">{speedUnit}</span>
          </div>
          <small className="text-muted">Kecepatan yang Terbaca oleh Radar</small>
        </div>
        <div className='card'>
          <div className='card-inner'>
            <h3>Train Position</h3>
            <MdTrain className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2>{totalDistance.toFixed(2)}</h2>
            <span className="unit">km</span>
          </div>
          <small className="text-muted">Posisi terhadap Jarak</small>
        </div>
        <div className='card'>
          <div className='card-inner'>
            <h3>Blocking</h3>
            <MdLocationOn className='card_icon' />
          </div>
          <div className="d-flex align-items-center">
            <h2>{rfidData.length > 0 ? rfidData[rfidData.length - 1].name:'Stand by ...'}</h2> {/* untuk dihubungkan dengan sensor */}
            <h3>{rfidData.length > 0 ? rfidData[rfidData.length - 1].tag_id:'Reading ...'}</h3>
          </div>
          <small className="text-muted">Posisi Kereta</small>
        </div>
      </div>
      <div className='charts-wrapper'>
        <div className='line-chart'>
          <ResponsiveContainer width="100%" height="100%">
            <h3>Grafik kecepatan terhadap jarak</h3>
            <LineChart
              width={500}
              height={300}
              data={distanceData}
              margin={{
                top: 5,
                right: 30,
                left: -30,
                bottom: 5,
              }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="distance" label={{ value: "Distance (Km)", position: 'insideBottomRight', offset: 0 }} />
              <YAxis label={{ value: "Kecepatan (km/h)", angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="speed" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className='gauge-chart' style={{ flex: 1, maxWidth: '500px' }}>
          <h3>Gauge Chart</h3>
          <GaugeComponent
            arc={{
              nbSubArcs: gaugeLimits.length,
              colorArray: gaugeLimits.map(limit => limit.color),
              width: 0.3,
              padding: 0.003
            }}
            labels={{
              valueLabel: {
                fontSize: 40,
                formatTextValue: value => `${value.toFixed(2)} km/h`
              }
            }}
            value={gaugeValue}
            maxValue={MAX_SPEED}
          />
        </div>
      </div>
    </main>
  );
}

export default Home;
