#!/usr/bin/env python3

import pandas as pd
import random as rd

class generate_ROTA:

	def __init__(self):

		self.tasks = {'Common areas':1, 'Common laundry':1, 'Office':1, 'Breakfast':2, 'Lunch':3, 'Dinner':3, 'Bins':2, 'Garden':2}
		self.we_tasks = {'Breakfast':2, 'Lunch':3, 'Dinner':3, 'Bins':2}
		self.days_dict = {'mon': 'Monday', 'tue':'Tuesday', 'wed':'Wednesday', 'thu':'Thursday', 'fri':'Friday', 'sat':'Saturday', 'sun':'Sunday'}

		self.ROTA = pd.DataFrame(columns=('Tasks', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
		self.ROTA['Tasks'] = self.tasks.keys()

		self.to_pick_next = [] # people who haven't been picked last round, so have to get picked the next round but another day


	# Read the input excel sheet, and initialize a couple of variables
	def readExcel(self):
		df = pd.read_excel('rota.xlsx')
		everyone = df['People'] # List of people that are in the base and can be selected for ROTAs
		availability = df['Availability']

		self.availabilities = {}
		self.people = []

		# Remove people that are not at base
		# And create a dict with everyone availability
		for idx, p in enumerate(everyone):
			p_availability = availability[idx]
			#print(p_availability)

			if p_availability != 'not':
				self.people.append(p)
				self.availabilities[p] = p_availability

		self.adaptPeoplePerTask()
		#print(f'people: {self.people}')


	def adaptPeoplePerTask(self):
		sum_ = sum(self.tasks.values())*5 + sum(self.we_tasks.values())*2

		iteration = 0
		while sum_ > 3.5*len(self.people) or iteration == 3:
			iteration += 1

			for k in self.tasks.keys():
				if self.tasks[k] == 1:
					pass

				else:
					self.tasks[k] = self.tasks[k] -1

			for k in self.we_tasks.keys():
				if self.we_tasks[k] == 1:
					pass
				else:
					self.we_tasks[k] = self.we_tasks[k] -1

			sum_ = sum(self.tasks.values())*5 + sum(self.we_tasks.values())*2

			if iteration == 2:
				break 		

	# Generate a list with all the people not available for the current day
	def generateNotAvailable(self, day):
		self.not_available_today = []

		for p in self.people:

			if self.availabilities[p] != self.availabilities[p]:
				
				pass

			elif day in self.availabilities[p]:

				self.not_available_today.append(p)

	# Select n people to do the selected task
	# Sample without replacement 
	# Return the people picked and the update people_subet
	def pick(self, amount_to_pick, people_subset, picked_already):
		# From people_subset remove the people who already have a ROTA this day and those not at the base
		tmp = [x for x in people_subset if x not in picked_already]
		pickable = [x for x in tmp if x not in self.not_available_today] 
		number_pickable = len(pickable)

		if number_pickable < amount_to_pick:

			# Reset the people_subset and pick the required additional amount of people
			self.to_pick_next = pickable
			people_subset = [x for x in self.people if x not in self.to_pick_next]

			tmp = [x for x in people_subset if x not in picked_already]
			pickable = [x for x in tmp if x not in self.not_available_today] 

			missing_amount = amount_to_pick - number_pickable # Number of people missing to reach amount_to_pick
			picked = rd.sample(pickable, missing_amount)
			
			picked.extend(self.to_pick_next)

		else: 

			picked = rd.sample(pickable, amount_to_pick)

		return picked, [x for x in people_subset if x not in picked]

	# Main function of the class
	# Generates the ROTA sheet
	def generateROTA(self):
		people_subset = self.people.copy()

		for day in self.days_dict.keys():

			self.generateNotAvailable(day)
			daily_rota = [] # People selected for the ROTA for this day
			picked_already = [] # People who already have a ROTA this day, to prevent people having 2 ROTAs

			# ROTA for the week end are different from week days
			if day in ['sat', 'sun']:

				daily_rota.extend(['', '', ''])
				for task in self.we_tasks.keys():

					amount_to_pick = self.we_tasks[task]
					
					picked, people_subset = self.pick(amount_to_pick, people_subset, picked_already)
					daily_rota.append(picked)
					picked_already.extend(picked)

				daily_rota.append('')

			# Generate ROTA for week day
			else:

				for task in self.tasks.keys():

					amount_to_pick = self.tasks[task]
					
					picked, people_subset = self.pick(amount_to_pick, people_subset, picked_already)
					daily_rota.append(picked)
					picked_already.extend(picked)

			self.ROTA[self.days_dict[day]] = daily_rota

	# Save the ROTA as a CSV file
	def saveROTA(self):
		self.ROTA.to_csv('ROTA.csv', index=False) 


def main():
	rota_generator = generate_ROTA()
	rota_generator.readExcel()

	rota_generator.generateROTA()
	rota_generator.saveROTA()

if __name__ == '__main__':
	main()