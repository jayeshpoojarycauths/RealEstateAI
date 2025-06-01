import React, { useEffect, useState } from "react";
import {
  Card,
  CardBody,
  Typography,
  Button,
  Input,
  Select,
  Option,
  Alert,
} from "../components/SafeMTW";
import api from "../services/api";

const defaultConfig = {
  sources: [],
  locations: [],
  property_types: [],
  price_range: { min: 0, max: 10000000 },
  max_pages: 10,
  interval_hours: 24,
};

export const LeadsScraperPage: React.FC = () => {
  const [config, setConfig] = useState<any>(defaultConfig);
  const [leadType, setLeadType] = useState<string>("property");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [results, setResults] = useState<any>(null);
  const [status, setStatus] = useState<string>("");
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [availablePropertyTypes, setAvailablePropertyTypes] = useState<
    string[]
  >([]);
  const [availableLocations, setAvailableLocations] = useState<string[]>([]);
  // Placeholder for logs
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    fetchConfig();
    fetchResults();
    fetchAvailableOptions();
    // fetchLogs(); // Placeholder for logs endpoint
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const res = await api.get("/scraping/config");
      setConfig(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to fetch config");
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const res = await api.get("/scraping/results");
      setResults(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to fetch results");
    }
  };

  const fetchAvailableOptions = async () => {
    // Placeholder: implement endpoints for these
    // const sources = await api.get('/scraping/sources');
    // setAvailableSources(sources.data);
    // const types = await api.get('/scraping/property-types');
    // setAvailablePropertyTypes(types.data);
    // const locations = await api.get('/scraping/locations');
    // setAvailableLocations(locations.data);
    setAvailableSources(["magicbricks", "housing", "proptiger", "commonfloor"]);
    setAvailablePropertyTypes(["apartment", "villa", "plot"]);
    setAvailableLocations(["Mumbai", "Bangalore", "Delhi"]);
  };

  const handleConfigChange = (field: string, value: any) => {
    setConfig((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSaveConfig = async () => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await api.post("/scraping/config", config);
      setSuccess("Configuration saved!");
      fetchConfig();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to save config");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateConfig = async () => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await api.put("/scraping/config", config);
      setSuccess("Configuration updated!");
      fetchConfig();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to update config");
    } finally {
      setLoading(false);
    }
  };

  const handleStartScraping = async () => {
    setStatus("Starting...");
    try {
      let response;
      if (leadType === "property") {
        response = await api.post("/scraping/start", { lead_type: leadType });
        setStatus("Property scraping started!");
        fetchResults();
      } else if (leadType === "user") {
        // Use the first selected location or empty string
        const location =
          config.locations && config.locations.length > 0
            ? config.locations[0]
            : "";
        response = await api.post("/scraped-leads/scrape-users", {
          location,
          max_pages: config.max_pages,
        });
        setStatus("User scraping complete!");
        setResults(response.data);
      } else if (leadType === "location") {
        response = await api.post("/scraped-leads/scrape-locations", {
          max_pages: config.max_pages,
        });
        setStatus("Location scraping complete!");
        setResults(response.data);
      }
    } catch (e: any) {
      setStatus("Failed to start scraping");
    }
  };

  const handleScheduleScraping = async () => {
    setStatus("Scheduling...");
    try {
      await api.post("/scraping/schedule", {
        interval_hours: config.interval_hours,
        lead_type: leadType,
      });
      setStatus("Scraping scheduled!");
    } catch (e: any) {
      setStatus("Failed to schedule scraping");
    }
  };

  const handleStopScraping = async () => {
    setStatus("Stopping...");
    try {
      await api.post("/scraping/stop");
      setStatus("Scraping stopped!");
    } catch (e: any) {
      setStatus("Failed to stop scraping");
    }
  };

  return (
    <div className="space-y-6">
      <Typography variant="h4" color="blue-gray">
        Leads Scraper
      </Typography>
      {error && <Alert color="red">{error}</Alert>}
      {success && <Alert color="green">{success}</Alert>}
      {/* ScraperConfigForm */}
      <Card>
        <CardBody>
          <Typography variant="h6" color="blue-gray">
            Scraping Configuration
          </Typography>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <Select
              label="Lead Type"
              value={leadType}
              onChange={(val: any) => setLeadType(val)}
            >
              <Option value="property">Property</Option>
              <Option value="user">User</Option>
              <Option value="location">Location</Option>
            </Select>
            <Select
              label="Sources"
              value={config.sources}
              multiple
              onChange={(val: any) => handleConfigChange("sources", val)}
            >
              {availableSources.map((src) => (
                <Option key={src} value={src}>
                  {src}
                </Option>
              ))}
            </Select>
            <Select
              label="Property Types"
              value={config.property_types}
              multiple
              onChange={(val: any) => handleConfigChange("property_types", val)}
            >
              {availablePropertyTypes.map((type) => (
                <Option key={type} value={type}>
                  {type}
                </Option>
              ))}
            </Select>
            <Select
              label="Locations"
              value={config.locations}
              multiple
              onChange={(val: any) => handleConfigChange("locations", val)}
            >
              {availableLocations.map((loc) => (
                <Option key={loc} value={loc}>
                  {loc}
                </Option>
              ))}
            </Select>
            <div className="flex gap-2 items-center">
              <Input
                label="Min Price"
                type="number"
                value={config.price_range?.min || 0}
                onChange={(e) =>
                  handleConfigChange("price_range", {
                    ...config.price_range,
                    min: Number(e.target.value),
                  })
                }
              />
              <Input
                label="Max Price"
                type="number"
                value={config.price_range?.max || 0}
                onChange={(e) =>
                  handleConfigChange("price_range", {
                    ...config.price_range,
                    max: Number(e.target.value),
                  })
                }
              />
            </div>
            <Input
              label="Max Pages"
              type="number"
              value={config.max_pages}
              onChange={(e) =>
                handleConfigChange("max_pages", Number(e.target.value))
              }
            />
            <Input
              label="Interval (hours)"
              type="number"
              value={config.interval_hours}
              onChange={(e) =>
                handleConfigChange("interval_hours", Number(e.target.value))
              }
            />
          </div>
          <div className="flex gap-2 mt-4">
            <Button color="blue" onClick={handleSaveConfig}>
              Save Config
            </Button>
            <Button color="blue-gray" onClick={handleUpdateConfig}>
              Update Config
            </Button>
          </div>
        </CardBody>
      </Card>
      {/* ScraperControls */}
      <Card>
        <CardBody>
          <Typography variant="h6" color="blue-gray">
            Scraping Controls
          </Typography>
          <div className="flex gap-2 mt-4">
            <Button color="green" onClick={handleStartScraping}>
              Start Scraping
            </Button>
            <Button color="blue" onClick={handleScheduleScraping}>
              Schedule Scraping
            </Button>
            <Button color="red" onClick={handleStopScraping}>
              Stop Scraping
            </Button>
          </div>
          {status && <Typography className="mt-2">{status}</Typography>}
        </CardBody>
      </Card>
      {/* ScraperResultsTable */}
      <Card>
        <CardBody>
          <Typography variant="h6" color="blue-gray">
            Scraping Results
          </Typography>
          <div className="overflow-x-auto mt-4">
            {results ? (
              <table className="w-full min-w-max table-auto text-left">
                <thead>
                  <tr>
                    <th>Source</th>
                    <th>Lead Type</th>
                    <th>Timestamp</th>
                    <th>Total Properties</th>
                    <th>Status</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.values(results)
                    .flat()
                    .map((res: any, idx: number) => (
                      <tr key={idx}>
                        <td>{res.source}</td>
                        <td>{res.lead_type || "-"}</td>
                        <td>
                          {res.timestamp
                            ? new Date(res.timestamp).toLocaleString()
                            : "-"}
                        </td>
                        <td>{res.total_properties}</td>
                        <td>{res.status}</td>
                        <td>{res.error || "-"}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            ) : (
              <Typography>No results yet.</Typography>
            )}
          </div>
        </CardBody>
      </Card>
      {/* ScraperLogsTable (placeholder) */}
      <Card>
        <CardBody>
          <Typography variant="h6" color="blue-gray">
            Scraping Logs (Coming Soon)
          </Typography>
        </CardBody>
      </Card>
    </div>
  );
};

export default LeadsScraperPage;
