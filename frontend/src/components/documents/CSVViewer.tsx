import React, { useEffect, useState } from 'react';

interface CSVViewerProps {
  content: string;
  onLoad?: () => void;
  style?: React.CSSProperties;
}

const CSVViewer: React.FC<CSVViewerProps> = ({ content, onLoad, style }) => {
  const [csvData, setCsvData] = useState<string[][]>([]);
  const [headers, setHeaders] = useState<string[]>([]);

  useEffect(() => {
    if (content) {
      try {
        // Parse CSV content
        const lines = content.split('\n').filter(line => line.trim());
        const parsedData = lines.map(line => {
          // Simple CSV parsing (handles basic cases)
          const values = line.split(',').map(value => 
            value.trim().replace(/^"|"$/g, '') // Remove quotes
          );
          return values;
        });

        if (parsedData.length > 0) {
          setHeaders(parsedData[0]);
          setCsvData(parsedData.slice(1));
        }
        
        // Call onLoad after parsing
        if (onLoad) {
          onLoad();
        }
      } catch (error) {
        console.error('Error parsing CSV:', error);
        if (onLoad) {
          onLoad();
        }
      }
    }
  }, [content, onLoad]);

  if (csvData.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>No data to display</p>
      </div>
    );
  }

  return (
    <div className="overflow-auto" style={style}>
      <table className="min-w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-50">
            {headers.map((header, index) => (
              <th 
                key={index}
                className="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-700"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {csvData.map((row, rowIndex) => (
            <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {row.map((cell, cellIndex) => (
                <td 
                  key={cellIndex}
                  className="border border-gray-300 px-4 py-2 text-sm text-gray-900"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CSVViewer; 